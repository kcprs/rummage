typedef struct {
    int num_blorps;
    float avg_blorp;
    const char* just_some_chars;
} SomeStruct;

int main(int argc, char** argv) {
    char* its_an_arg = argv[0];
    int some_value = 1;
    float array[] = {1.f, 1.f, 2.f, 3.f};  // @loupe: break_main
    int a = some_value + argc;
    int* point = &some_value;
    (void)0;         // @loupe: deref_pointer
    some_value = 2;  // @loupe: index_int_array

    SomeStruct some_struct = {.num_blorps = 56,
                              .avg_blorp = 3.14f,
                              .just_some_chars = "look, it's a string!"};
    (void)0;  // @loupe: struct_children

    return 0;  // @loupe: break_main
}
