#include "llvm/Pass.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace
{

    struct LibraryCallPass : public PassInfoMixin<LibraryCallPass>
    {
        // counter for states
        int stateCounter = 0;

        // map from (state) to (map from transition to next state)
        std::unordered_map<int, std::unordered_map<std::string, std::vector<int>>> transitionTable;

        // map from (address of basic block) to (start state, final state)
        std::unordered_map<BasicBlock*, std::pair<int, int>> blockStates;

        // map from (function name) to (start state, final state)
        std::unordered_map<std::string, std::pair<int, int>> functionStates;

        // initial state
        int initialState;

        // Create an NFA for each basic block
        void buildBasicBlockNFA(BasicBlock &B)
        {
            int startState = stateCounter;
            // Iterate over instructions in the block
            for (auto &I : B)
            {
                if (CallInst *callInst = dyn_cast<CallInst>(&I))
                {
                    Function *calledFunc = callInst->getCalledFunction();
                    std::string functionName = calledFunc->getName().str();
                    int currentState = stateCounter;
                    int nextState = ++stateCounter;
                    if (transitionTable.find(currentState) == transitionTable.end())
                    {
                        transitionTable[currentState] = std::unordered_map<std::string, std::vector<int>>();
                    }
                    if (transitionTable[currentState].find(functionName) == transitionTable[currentState].end())
                    {
                        transitionTable[currentState][functionName] = std::vector<int>();
                    }
                    transitionTable[currentState][functionName].push_back(nextState);
                }
            }
            int finalState = stateCounter;
            blockStates[&B] = {startState, finalState};
        }

        // Create an NFA for each function
        void buildFunctionNFA(Function &F)
        {
            // Iterate over basic blocks in the function
            for (auto &B : F)
            { 
                buildBasicBlockNFA(B);
            }

            // Iterate over basic blocks in the function again to join them with epsilon transitions
            for (auto &B : F)
            {
                // Get the final state of this basic block
                    int finalState = blockStates[&B].second;

                // Get the successors of this basic block
                for (auto *succ : successors(&B))
                {
                    // Get the start state of the successor basic block
                    int startState = blockStates[succ].first;

                    // skip if finalState == startState
                    if (finalState == startState)
                    {
                        continue;
                    }

                    // Add an epsilon transition
                    if (transitionTable.find(finalState) == transitionTable.end())
                    {
                        transitionTable[finalState] = std::unordered_map<std::string, std::vector<int>>();
                    }
                    if (transitionTable[finalState].find("") == transitionTable[finalState].end())
                    {
                        transitionTable[finalState][""] = std::vector<int>();
                    }
                    transitionTable[finalState][""].push_back(startState);
                }                
            }
        }

        // Run on the entire module
        PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM)
        {
            // list of user-defined functions
            std::vector<std::string> userFunctions;

            // Build NFA for each function
            for (Function &F : M)
            {
                if (!F.isDeclaration())
                {
                    // store the name of the user-defined function
                    userFunctions.push_back(F.getName().str());

                    int startState = stateCounter;
                    buildFunctionNFA(F);
                    int finalState = stateCounter;

                    // if the function is 'main', mark its start state as the initial state
                    if (F.getName().str() == "main")
                    {
                        initialState = startState;
                    }

                    // store the start and final states of the function
                    functionStates[F.getName().str()] = {startState, finalState};

                    // increment the state counter (to avoid overlapping states)
                    stateCounter++;
                }
            }

            // (state, transition) pairs to be deleted
            std::vector<std::pair<int, std::string>> toDelete;

            // loop over every transition and replace transitions with user-functions with epsilon transitions to their own NFAs
            for (auto &state : transitionTable)
            {
                for (auto &transition : state.second)
                {
                    // get the function name for the transition
                    std::string functionName = transition.first;

                    // check if the function is a user-defined function
                    if (std::find(userFunctions.begin(), userFunctions.end(), functionName) != userFunctions.end())
                    {
                        // get the start and final states of the function
                        int startState = functionStates[functionName].first;
                        int finalState = functionStates[functionName].second;

                        // replace the transition with an epsilon transition to the function's NFA
                        transitionTable[state.first][""] = {startState};

                        // add an epsilon transition from the function's final state to the next states
                        if (transitionTable.find(finalState) == transitionTable.end())
                        {
                            transitionTable[finalState] = std::unordered_map<std::string, std::vector<int>>();
                        }
                        if (transitionTable[finalState].find("") == transitionTable[finalState].end())
                        {
                            transitionTable[finalState][""] = std::vector<int>();
                        }
                        transitionTable[finalState][""].insert(transitionTable[finalState][""].end(), transition.second.begin(), transition.second.end());

                        // remove the previous transition from the transition table
                        toDelete.push_back({state.first, transition.first});
                    }
                }
            }

            // delete the transitions that were replaced
            for (auto &p : toDelete)
            {
                transitionTable[p.first].erase(p.second);
            }

            // print the NFA in Graphviz format
            printToGraphviz(outs(), &M);

            outs() << "\n\n-------------------\n\n";

            // print the transition table
            outs() << initialState << "\n";
            for (const auto &state : transitionTable)
            {
                for (const auto &transition : state.second)
                {
                    for (int nextState : transition.second)
                    {
                        std::string transitionLabel = transition.first;
                        if (transitionLabel == "")
                        {
                            transitionLabel = "0";
                        }
                        outs() << state.first << " " << transitionLabel << " " << nextState << "\n";
                    }
                }
            }

            return PreservedAnalyses::all();
        };

        // create a Graphviz representation of the NFA
        void printToGraphviz(raw_ostream &OS, const Module *M) const
        {
            OS << "digraph NFA {\n";
            OS << "  rankdir=LR;\n";
            // splines=curved and overlap=false to make the graph more readable
            OS << "  splines=true;\n";
            OS << "  overlap=false;\n";
            OS << "  node [shape = circle];\n";
            OS << "  node [label=\"\"];\n";
            for (const auto &state : transitionTable)
            {
                for (const auto &transition : state.second)
                {
                    for (int nextState : transition.second)
                    {
                        std::string transitionLabel = transition.first;
                        if (transitionLabel == "")
                        {
                            transitionLabel = "&epsilon;";
                        }
                        OS << "  " << state.first << " -> " << nextState << " [label=\"" << transitionLabel << "\"];\n";
                    }
                }
            }
            // make an arrow go into the initial state
            OS << "  empty [label=\"\", shape=none];\n";
            OS << "  empty -> " << initialState << ";\n";
            OS << "}\n";
        }
    };
}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo()
{
    return {
        .APIVersion = LLVM_PLUGIN_API_VERSION,
        .PluginName = "Library call pass",
        .PluginVersion = "v0.1",
        .RegisterPassBuilderCallbacks = [](PassBuilder &PB)
        {
            PB.registerPipelineStartEPCallback(
                [](ModulePassManager &MPM, OptimizationLevel Level)
                {
                    MPM.addPass(LibraryCallPass());
                });
        }};
}
