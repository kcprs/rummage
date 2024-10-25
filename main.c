int main(int argc, char** argv) {
    char* its_an_arg = argv[0];
    int some_value = 1;
    float array[] = {1.f, 1.f, 2.f, 3.f};  // @loupe: break_main
    int a = some_value + argc;
    some_value = 2; // @loupe: index_int_array

    return 0;  // @loupe: break_main
}
