// Seeded RNG helpers (deterministic output)

// Mulberry32 PRNG
function mulberry32(seed) {
  let t = seed >>> 0;
  return function rand() {
    t += 0x6d2b79f5;
    let x = t;
    x = Math.imul(x ^ (x >>> 15), x | 1);
    x ^= x + Math.imul(x ^ (x >>> 7), x | 61);
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

function randRange(rng, a, b) {
  return a + (b - a) * rng();
}

function randInt(rng, a, bInclusive) {
  return Math.floor(randRange(rng, a, bInclusive + 1));
}

function randChoice(rng, arr) {
  return arr[Math.floor(rng() * arr.length)];
}

function jitter(rng, amount) {
  return (rng() * 2 - 1) * amount;
}
