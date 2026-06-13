/* usage:  qube <file.function|file.spec> [depths...]
 *   - 입력 치환을 합성하여 {name}_out.real 을 생성
 *   - 회로를 입력에 적용해 항등 검증, 게이트 수 출력
 *
 * build:  gcc -O3 -std=c11 -o qube unit_opers.c leaf_utils.c block_ops.c \
 *              exhaustive.c mixing.c reduction.c synthesis.c qube_main.c
 */
#include "synthesis.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static gate_t circuit[SYN_MAX_GATES];
static perm_t perm[MAX_PERM], chk[MAX_PERM];

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s <file.function|file.spec> [depths...]\n", argv[0]); return 2; }
    const char *path = argv[1];
    int len = 0, n;
    const char *dot = strrchr(path, '.');
    if (dot && strcmp(dot, ".spec") == 0) n = read_spec_file(path, perm, &len);
    else                                  n = read_function_file(path, perm, &len);
    if (n < 0) { fprintf(stderr, "failed to read %s\n", path); return 2; }

    int depths[20] = {0};
    int nd = argc - 2;
    for (int i = 0; i < nd && i < 20; i++) depths[i] = atoi(argv[2 + i]);
    if (nd > 0) for (int i = nd; i < 20; i++) depths[i] = depths[nd - 1];   /* 마지막 값으로 패딩 */

    int ng = alg_synthesis(n, perm, depths, circuit);

    /* Toffoli 게이트 수: 제어 m(>1)개 게이트는 2m-3 개의 기본 Toffoli 로 분해됨 (core.py show_Qube_gates 와 동일) */
    long n_tof = 0;
    for (int i = 0; i < ng; i++) { int c = circuit[i].n_ctrl; if (c > 1) n_tof += 2 * c - 3; }

    /* {name}_out.real 출력 */
    char outpath[1024];
    snprintf(outpath, sizeof outpath, "%s", path);
    char *od = strrchr(outpath, '.'); if (od) *od = '\0';
    strncat(outpath, "_out.real", sizeof(outpath) - strlen(outpath) - 1);
    write_real_format(n, circuit, ng, outpath);

    /* 검증 */
    memcpy(chk, perm, (size_t)(1 << n) * sizeof(perm_t));
    apply_circuit(n, chk, circuit, ng);
    int ident = 1; for (int i = 0; i < (1 << n); i++) if (chk[i] != (perm_t)i) { ident = 0; break; }

    printf("Target file\t: %s\n", path);
    printf("# of bits\t: %d\n", n);
    printf("# of gates\t: %d\n", ng);
    printf("# of Toffoli\t: %ld\n", n_tof);
    printf("output\t\t: %s\n", outpath);
    if (!ident) printf("Not equal!\n");
    else        printf("verified\t: identity OK\n");
    return ident ? 0 : 1;
}
