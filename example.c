#include <stdio.h>
#include <stdlib.h>

void bar() {
    int x;
    scanf("%d", &x);
    if (x) {
        scanf("%d", &x);
    }
}

void foo() {
    printf("Hello, World!\n");
    bar();
}

void baz() {
    return;
}

int main() {
    foo();
    int x;
    scanf("%d", &x);
    while(x) {
        malloc(100);
    }
    printf("Goodbye, World!\n");
    return 0;
}
