#ifndef UNIT_OPERS_H
#define UNIT_OPERS_H

#include <stdint.h>
#include <stddef.h>

#define MAXN        16            /* 지원 최대 비트 수 */
#define MAX_PERM    (1u << MAXN)  /* 65536 */
#define MAX_CTRL    (MAXN + 2)    /* 게이트당 제어비트 상한. 측정상 최대 n-1<=15, 여유 포함 */
#define MAX_CONS    (MAXN + 2)    /* cons 리스트 최대 길이 */

/* ---- 치환(permutation) ---- */
typedef uint32_t perm_t;

/* ---- 게이트 ----
 * Python: [target, [[ctrl_bit, val], ...]]
 *  - null 게이트(Python의 [])는 n_ctrl == -1 로 표현.
 *  - 제어 없는 X 게이트(Python의 [t, []])는 n_ctrl == 0.
 */
typedef struct {
    int target;
    int n_ctrl;                 /* -1 이면 null 게이트 */
    int ctrl_bit[MAX_CTRL];
    int ctrl_val[MAX_CTRL];     /* 0 또는 1 */
} gate_t;

/* ---- returnOptions 결과 항목 ----
 * Python: [[i, i+1], parity]
 */
typedef struct {
    int v0, v1;
    int parity;                 /* 0, 1, 또는 2(collision) */
} option_t;

/* ---- cons (제약 문자열 리스트) ----
 * 각 항목은 길이 len('0'/'1'/'-')의 NUL 종료 문자열.
 */
typedef struct {
    char s[MAX_CONS][MAXN + 1];
    int  count;
} cons_t;

/* =======================================================================
 * 게이트 헬퍼
 * ===================================================================== */
void  gate_set_null(gate_t *g);
int   gate_is_null(const gate_t *g);
void  gate_init(gate_t *g, int target);            /* 제어 없는 게이트로 초기화 */
void  gate_add_ctrl(gate_t *g, int bit, int val);  /* 제어비트 추가 (순서 보존) */
int   gate_eq(const gate_t *a, const gate_t *b);   /* Python == 동치 비교 */

/* =======================================================================
 * 치환 기초 연산
 * ===================================================================== */

/* sbox[idx]==val 인 idx 반환. inv 가 NULL 이면 선형 탐색, 아니면 O(1). */
int   perm_index(const perm_t *sbox, int len, perm_t val, const int *inv);

/* inv[sbox[i]] = i 채우기. (len 길이) */
void  perm_build_inv(const perm_t *sbox, int len, int *inv);

/* sbox == [0,1,...,len-1] 이면 1. */
int   perm_is_identity(const perm_t *sbox, int len);

/* =======================================================================
 * 기초 연산 (core.py 대응)
 * ===================================================================== */

/* apply_gate(n, sbox, gate): sbox 를 제자리(in-place)에서 변형. (Python 은 deepcopy 반환) */
void  apply_gate(int n, perm_t *sbox, const gate_t *g);

/* gate_to_index(n, gate, index) */
int   gate_to_index(int n, const gate_t *g, int index);

/* returnOptions(n, sbox) -> out[], 반환값은 항목 수 (= 1<<(n-1)).
 * out 은 최소 (1<<(n-1)) 크기여야 함. */
int   return_options(int n, const perm_t *sbox, option_t *out);

/* parityOfSbox(n, sbox): 홀치환이면 1, 짝치환이면 0. */
int   parity_of_sbox(int n, const perm_t *sbox);

/* =======================================================================
 * cons 연산
 * ===================================================================== */
void  cons_clear(cons_t *c);
void  cons_push(cons_t *c, const char *s);                 /* 문자열 1개 추가 */

/* next_position(n, cons) -> out (길이 n + NUL). out 버퍼는 MAXN+1 이상. */
void  next_position(int n, const cons_t *c, char *out);

/* cons_update(n, cons): cons 를 제자리에서 병합 갱신. */
void  cons_update(int n, cons_t *c);

/* conditions_and(n, cons) -> out (길이 n + NUL). */
void  conditions_and(int n, const cons_t *c, char *out);

/* =======================================================================
 * 파일 입출력
 * ===================================================================== */

/* .function 파일("[a, b, c, ...]") 읽기.
 *  sbox 에 값 저장, *out_len 에 길이, 반환값 n (= log2(len)). 실패 시 -1. */
int   read_function_file(const char *path, perm_t *sbox, int *out_len);

/* .spec 파일(진리표) 읽기. 반환값 n, 실패 시 -1. */
int   read_spec_file(const char *path, perm_t *sbox, int *out_len);

/* 길이로부터 n 계산 (len 이 2의 거듭제곱이라 가정). 아니면 -1. */
int   bits_from_len(int len);

#endif /* UNIT_OPERS_H */
