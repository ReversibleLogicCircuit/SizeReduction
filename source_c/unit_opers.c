#include "unit_opers.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ===== 게이트 헬퍼 ===== */
void gate_set_null(gate_t *g) { g->target = -1; g->n_ctrl = -1; }
int  gate_is_null(const gate_t *g) { return g->n_ctrl < 0; }
void gate_init(gate_t *g, int target) { g->target = target; g->n_ctrl = 0; }
void gate_add_ctrl(gate_t *g, int bit, int val) {
    int k = g->n_ctrl;
    g->ctrl_bit[k] = bit; g->ctrl_val[k] = val; g->n_ctrl = k + 1;
}
int gate_eq(const gate_t *a, const gate_t *b) {
    if (gate_is_null(a) || gate_is_null(b))
        return gate_is_null(a) && gate_is_null(b);
    if (a->target != b->target || a->n_ctrl != b->n_ctrl) return 0;
    for (int i = 0; i < a->n_ctrl; i++)
        if (a->ctrl_bit[i] != b->ctrl_bit[i] || a->ctrl_val[i] != b->ctrl_val[i]) return 0;
    return 1;
}

/* ===== 치환 기초 연산 ===== */
int perm_index(const perm_t *sbox, int len, perm_t val, const int *inv) {
    if (inv) return inv[val];
    for (int i = 0; i < len; i++) if (sbox[i] == val) return i;
    return -1;
}
void perm_build_inv(const perm_t *sbox, int len, int *inv) {
    for (int i = 0; i < len; i++) inv[sbox[i]] = i;
}
int perm_is_identity(const perm_t *sbox, int len) {
    for (int i = 0; i < len; i++) if (sbox[i] != (perm_t)i) return 0;
    return 1;
}

static int py_slice(const char *vals, int num, int a, int b, char *dst, int dp) {
    if (a < 0) a += num;
    if (a < 0) a = 0; else if (a > num) a = num;
    if (b < 0) b += num;
    if (b < 0) b = 0; else if (b > num) b = num;
    for (int t = a; t < b; t++) dst[dp++] = vals[t];
    return dp;
}

void apply_gate(int n, perm_t *sbox, const gate_t *g) {
    if (gate_is_null(g)) return;
    int L = 1 + g->n_ctrl;
    int num = n - L;
    if (num < 0) return;                 /* 퇴화: Python 이라면 예외. 유효 입력에선 발생 안 함 */

    {
        unsigned used = 1u << g->target, dup = 0, cmask = 0, cval = 0;
        for (int k = 0; k < g->n_ctrl; k++) {
            unsigned cb = 1u << g->ctrl_bit[k];
            if (used & cb) { dup = 1; break; }
            used |= cb; cmask |= cb;
            if (g->ctrl_val[k]) cval |= cb;
        }
        if (!dup) {
            const unsigned full = (1u << n) - 1u;
            const unsigned tmask = 1u << g->target;
            const unsigned freemask = full & ~(tmask | cmask);
            const unsigned base = cval;          /* 제어=값, target=0, free=0 */
            unsigned sub = freemask;
            while (1) {
                unsigned idx = base | sub;
                unsigned j = idx | tmask;
                perm_t t = sbox[idx]; sbox[idx] = sbox[j]; sbox[j] = t;
                if (sub == 0) break;
                sub = (sub - 1u) & freemask;
            }
            return;
        }
    }

    int  pbit[1 + MAX_CTRL];
    char pval[1 + MAX_CTRL];
    pbit[0] = n - g->target - 1; pval[0] = '-';
    for (int k = 0; k < g->n_ctrl; k++) {
        pbit[k + 1] = n - g->ctrl_bit[k] - 1;
        pval[k + 1] = (char)('0' + g->ctrl_val[k]);
    }
    /* pbit 오름차순 안정 정렬 (동률은 원래 순서 유지) */
    for (int i = 1; i < L; i++) {
        int b = pbit[i]; char v = pval[i]; int j = i - 1;
        while (j >= 0 && pbit[j] > b) { pbit[j+1] = pbit[j]; pval[j+1] = pval[j]; j--; }
        pbit[j+1] = b; pval[j+1] = v;
    }
    for (int i = 1; i < L; i++) pbit[i] -= i;   /* 삽입 오프셋 보정 */

    char vals[MAXN + 1], tarNum[2 * MAXN + 2];
    for (int i = 0; i < (1 << num); i++) {
        for (int t = 0; t < num; t++) vals[t] = (char)('0' + ((i >> (num - 1 - t)) & 1));
        vals[num] = '\0';
        int tp = 0;
        tp = py_slice(vals, num, 0, pbit[0], tarNum, tp);
        tarNum[tp++] = pval[0];
        for (int j = 0; j < L - 1; j++) {
            tp = py_slice(vals, num, pbit[j], pbit[j+1], tarNum, tp);
            tarNum[tp++] = pval[j+1];
        }
        tp = py_slice(vals, num, pbit[L-1], num, tarNum, tp);
        tarNum[tp] = '\0';

        int dash = -1;
        for (int t = 0; t < tp; t++) if (tarNum[t] == '-') { dash = t; break; }
        int num1 = 0, num2 = 0;
        for (int t = 0; t < tp; t++) {
            int b0, b1;
            if (t == dash) { b0 = 0; b1 = 1; }
            else { b0 = b1 = tarNum[t] - '0'; }
            num1 = (num1 << 1) | b0;
            num2 = (num2 << 1) | b1;
        }
        perm_t tmp = sbox[num1]; sbox[num1] = sbox[num2]; sbox[num2] = tmp;
    }
}

/* ===== gate_to_index ===== */
int gate_to_index(int n, const gate_t *g, int index) {
    (void)n;
    if (gate_is_null(g)) return index;
    for (int k = 0; k < g->n_ctrl; k++)
        if (((index >> g->ctrl_bit[k]) & 1) != g->ctrl_val[k]) return index;
    return index ^ (1 << g->target);
}

/* ===== returnOptions =====
 * i, i+1 의 현재 위치 패리티가 다르면 그 패리티, 같으면 2. 위치는 inv 로 O(1). */
int return_options(int n, const perm_t *sbox, option_t *out) {
    const int len = 1 << n;
    static int inv[MAX_PERM];
    perm_build_inv(sbox, len, inv);
    int cnt = 0;
    for (int i = 0; i < len; i += 2) {
        int p0 = inv[i] & 1, p1 = inv[i + 1] & 1;
        out[cnt].v0 = i; out[cnt].v1 = i + 1;
        out[cnt].parity = (p0 != p1) ? p0 : 2;
        cnt++;
    }
    return cnt;
}

/* ===== parityOfSbox (선택정렬 transposition 수의 홀짝) ===== */
static int perm_cmp_(const void *a, const void *b) {
    perm_t x = *(const perm_t *)a, y = *(const perm_t *)b;
    return (x > y) - (x < y);
}
int parity_of_sbox(int n, const perm_t *sbox) {
    const int len = 1 << n;
    static perm_t work[MAX_PERM], want[MAX_PERM];
    static int posmap[MAX_PERM];
    for (int i = 0; i < len; i++) { work[i] = sbox[i]; want[i] = sbox[i]; }
    qsort(want, (size_t)len, sizeof(perm_t), perm_cmp_);   /* wantForm = sorted(sbox) */
    for (int i = 0; i < len; i++) posmap[work[i]] = i;     /* 값 -> 현재 위치 (값 < 2^n) */
    int count = 0;
    for (int i = 0; i < len; i++) {
        if (want[i] != work[i]) {
            count++;
            int pos = posmap[want[i]];
            perm_t moved = work[i];
            work[pos] = moved; work[i] = want[i];
            posmap[moved] = pos; posmap[want[i]] = i;
        }
    }
    return count & 1;
}

/* ===== cons 연산 ===== */
void cons_clear(cons_t *c) { c->count = 0; }
void cons_push(cons_t *c, const char *s) {
    int i = 0;
    for (; i < MAXN && s[i]; i++) c->s[c->count][i] = s[i];
    c->s[c->count][i] = '\0';
    c->count++;
}
static int str_count_dash(const char *s) {
    int n = 0; for (const char *p = s; *p; p++) if (*p == '-') n++; return n;
}
static int str_index_dash(const char *s) {
    for (int i = 0; s[i]; i++)
        if (s[i] == '-') return i;
    return -1;
}
void next_position(int n, const cons_t *c, char *out) {
    if (c->count == 0) {
        for (int i = 0; i < n - 1; i++) out[i] = '0';
        out[n - 1] = '-'; out[n] = '\0'; return;
    }
    const char *target = c->s[c->count - 1];
    int pos = str_index_dash(target);
    int k = 0;
    for (int i = 0; i < pos - 1; i++) out[k++] = target[i];
    out[k++] = '1';
    for (int i = 0; i < n - pos - 1; i++) out[k++] = '0';
    out[k++] = '-'; out[k] = '\0';
}
void cons_update(int n, cons_t *c) {
    while (c->count > 1 &&
           str_count_dash(c->s[c->count - 1]) == str_count_dash(c->s[c->count - 2])) {
        char c1[MAXN + 1];
        strcpy(c1, c->s[c->count - 1]);
        c->count -= 2;
        int pos = str_index_dash(c1);
        char merged[MAXN + 1];
        int k = 0;
        for (int i = 0; i < pos - 1; i++) merged[k++] = c1[i];
        for (int i = 0; i < n - pos + 1; i++) merged[k++] = '-';
        merged[k] = '\0';
        cons_push(c, merged);
    }
}
void conditions_and(int n, const cons_t *c, char *out) {
    for (int i = 0; i < n; i++) {
        int flag = 1;
        for (int j = 0; j < c->count; j++)
            if (c->s[j][i] != '0') { flag = 0; break; }
        out[i] = flag ? '0' : '-';
    }
    out[n] = '\0';
}

/* ===== bits_from_len ===== */
int bits_from_len(int len) {
    if (len <= 0 || (len & (len - 1)) != 0) return -1;
    int n = 0; while ((1 << n) < len) n++; return n;
}

/* ===== 파일 입출력 ===== */
static char *slurp(const char *path) {
    FILE *fp = fopen(path, "rb");
    if (!fp) return NULL;
    fseek(fp, 0, SEEK_END);
    long sz = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    if (sz < 0) { fclose(fp); return NULL; }
    char *buf = (char *)malloc((size_t)sz + 1);
    if (!buf) { fclose(fp); return NULL; }
    size_t rd = fread(buf, 1, (size_t)sz, fp);
    buf[rd] = '\0';
    fclose(fp);
    return buf;
}
int read_function_file(const char *path, perm_t *sbox, int *out_len) {
    char *buf = slurp(path);
    if (!buf) return -1;
    char *lb = strchr(buf, '[');
    char *rb = strrchr(buf, ']');
    if (!lb || !rb || rb <= lb) { free(buf); return -1; }
    *rb = '\0';
    int len = 0;
    char *p = lb + 1;
    while (*p) {
        while (*p && (*p < '0' || *p > '9') && *p != '-') p++;
        if (!*p) break;
        char *end;
        long v = strtol(p, &end, 10);
        if (end == p) break;
        if (len >= (int)MAX_PERM) { free(buf); return -1; }
        sbox[len++] = (perm_t)v;
        p = end;
    }
    free(buf);
    int n = bits_from_len(len);
    if (n < 0) return -1;
    if (out_len) *out_len = len;
    return n;
}
int read_spec_file(const char *path, perm_t *sbox, int *out_len) {
    char *buf = slurp(path);
    if (!buf) return -1;
    int len = 0;
    char *line = buf;
    while (line && *line) {
        char *nl = strchr(line, '\n');
        if (nl) *nl = '\0';
        if (line[0] != '.' && line[0] != '#' && line[0] != '\0' && line[0] != '\r') {
            perm_t v = 0;
            int valid = 0;
            for (char *q = line; *q; q++) {
                if (*q == '0' || *q == '1') { v = (v << 1) | (perm_t)(*q - '0'); valid = 1; }
                else if (*q == '\r' || *q == ' ' || *q == '\t') continue;
                else { valid = 0; break; }
            }
            if (valid) {
                if (len >= (int)MAX_PERM) { free(buf); return -1; }
                sbox[len++] = v;
            }
        }
        if (!nl) break;
        line = nl + 1;
    }
    free(buf);
    int n = bits_from_len(len);
    if (n < 0) return -1;
    if (out_len) *out_len = len;
    return n;
}
