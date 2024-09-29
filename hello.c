#include <stdio.h>
#include <stdlib.h>

void bar() {
    int x;
    scanf("%d", &x);  // Library call
    if (x) {
        scanf("%d", &x);  // Library call
    }
}

void foo() {
    printf("Hello, World!\n");  // Library call
    bar();  // Function call (should create an epsilon transition)
}

void baz() {
    return;
}

int main() {
    foo();  // Function call (should create an epsilon transition)
    while(1) {
        malloc(100);  // Library call
    }
    return 0;
}
