#include <stdbool.h>

typedef struct {
    int num_blorps;
    float avg_blorp;
    const char* just_some_chars;
} SomeStruct;

typedef int ImAnInt;

void test_int() {
    int one = 1;
    (void)0;  // @loupe: test_int
}

void test_float() {
    float half = 0.5f;
    (void)0;  // @loupe: test_float
}

void test_bool() {
    bool truth = true;
    bool lie = false;
    (void)0;  // @loupe: test_bool
}
struct TestStruct {
    int a;
    float b;
};

void test_struct() {
    struct TestStruct a_struct = {.a = 1, .b = 3.67f};
    (void)0;  // @loupe: test_struct
}

void run_tests() {
    test_int();
    test_float();
    test_bool();
    test_struct();
}

int main(int argc, char** argv) {
    char* its_an_arg = argv[0];
    ImAnInt some_value = 1;  // @loupe: just_checking
    bool im_a_bool = false;  // @loupe: just_checking
    float im_a_float = 4.8f;
    float array[] = {1.f, 1.f, 2.f, 3.f};  // @loupe: break_main
    int a = some_value + argc;
    int* point = &some_value;
    (void)0;         // @loupe: deref_pointer
    some_value = 2;  // @loupe: index_int_array

    SomeStruct some_struct = {.num_blorps = 56,
                              .avg_blorp = 3.14f,
                              .just_some_chars = "look, it's a string!"};
    (void)0;  // @loupe: struct_children
    (void)0;  // @loupe: break_main

    run_tests();
    return 0;
}
