#include "program.h"
#include "allfunctions.h"

int main(void)
{
    int answer	= square(2) + cube(3);

    printf("answer = %i\n", answer);

    assert(answer == 31);

    return EXIT_SUCCESS;
}
