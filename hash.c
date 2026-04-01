#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t rotate_left(uint64_t value, int shift) {
    return (value << shift) | (value >> (64 - shift));
}

/*
 * Educational custom hash:
 * - mixes password and salt
 * - applies repeated rounds to make brute-force slightly harder
 * - returns a fixed hexadecimal digest
 *
 * This is intentionally simple for an academic operating systems project.
 */
static uint64_t custom_hash(const char *password, const char *salt) {
    const uint64_t prime = 1099511628211ULL;
    uint64_t hash = 1469598103934665603ULL;
    uint64_t pepper = 0xA5A5F0F0C3C39696ULL;
    size_t password_length = strlen(password);
    size_t salt_length = strlen(salt);

    for (size_t i = 0; i < salt_length; i++) {
        hash ^= (unsigned char)salt[i];
        hash *= prime;
        hash = rotate_left(hash, 5) ^ pepper;
    }

    for (int round = 0; round < 4096; round++) {
        for (size_t i = 0; i < password_length; i++) {
            hash ^= (unsigned char)password[i] + (uint64_t)(round + 1);
            hash *= prime;
            hash = rotate_left(hash, 7) ^ (pepper + (uint64_t)round);
        }

        for (size_t i = 0; i < salt_length; i++) {
            hash ^= ((unsigned char)salt[i] << (i % 8));
            hash *= prime;
            hash = rotate_left(hash, 11) + (uint64_t)(round * 31);
        }
    }

    return hash ^ pepper ^ ((uint64_t)password_length << 32) ^ (uint64_t)salt_length;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <password> <salt>\n", argv[0]);
        return 1;
    }

    uint64_t digest = custom_hash(argv[1], argv[2]);
    printf("%016llx\n", (unsigned long long)digest);
    return 0;
}
