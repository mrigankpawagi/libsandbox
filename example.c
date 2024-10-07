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
    while(1) {
        malloc(100);
    }
    return 0;
}
