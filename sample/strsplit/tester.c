#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

extern  char    **strsplit(const char *line, int *nwords);
extern  void    free_words(char **words);

static void test_strsplit(const char *str)
{
    int  nwords;
    char **words   = strsplit(str, &nwords);

    printf("\"%s\" ->\n", str);
    for(int w=0 ; w<nwords ; ++w) {
        printf("\t[%i]  \"%s\"\n", w, words[w]);
    }
    free_words(words);
    printf("\n");
}

int main(int argc, char *argv[])
{
    test_strsplit("");
    test_strsplit("    ");
    test_strsplit("AllGood");
    test_strsplit("  AllGood");
    test_strsplit("AllGood  ");
    test_strsplit("  AllGood  ");
    test_strsplit("   Life is Good   ");
    test_strsplit("   Life is 'All Good'   ");
    test_strsplit("   Life is \"All Good\"   ");
    return 0;
}
