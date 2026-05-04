async function loadPrimes() {
  // Relative path is important for GitHub Pages project sites.
  const res = await fetch("./data/primes.json", { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to load primes.json: ${res.status} ${res.statusText}`);
  }
  return await res.json();
}

function digitsOf(nStr) {
  // assumes decimal string
  const s = nStr.replace(/^0+/, "") || "0";
  return s.length;
}

function lastDigits(nStr, k = 10) {
  const s = nStr.replace(/^0+/, "") || "0";
  return s.slice(-k).padStart(k, "0");
}

function modSmall(nStr, m) {
  // Compute n mod m for a large decimal string nStr (no BigInt required)
  let r = 0;
  for (const ch of nStr) {
    const d = ch.charCodeAt(0) - 48;
    if (d < 0 || d > 9) continue;
    r = (r * 10 + d) % m;
  }
  return r;
}

function formatModChecks(nStr) {
  // small sanity checks: primes > 5 will not be divisible by 2 or 5
  const mods = [2, 3, 5, 7, 11, 13, 17, 19];
  const parts = mods.map(m => `${m}:${modSmall(nStr, m)}`);
  return parts.join("  ");
}

function setPrimeUI(sample) {
  const primeStr = sample.prime;
  const meta = document.getElementById("primeMeta");
  const primeValue = document.getElementById("primeValue");
  const digitsValue = document.getElementById("digitsValue");
  const lastDigitsValue = document.getElementById("lastDigitsValue");
  const modChecksValue = document.getElementById("modChecksValue");

  meta.textContent = `Label: ${sample.label ?? "prime"}   |   Source: ${sample.source ?? "static"}   |   Notes: ${sample.notes ?? "—"}`;
  primeValue.textContent = primeStr;

  digitsValue.textContent = `${digitsOf(primeStr)}`;
  lastDigitsValue.textContent = lastDigits(primeStr, 10);
  modChecksValue.textContent = formatModChecks(primeStr);
}

function copyTextToClipboard(text) {
  // Modern browsers
  if (navigator.clipboard?.writeText) {
    return navigator.clipboard.writeText(text);
  }
  // Fallback
  const ta = document.createElement("textarea");
  ta.value = text;
  document.body.appendChild(ta);
  ta.select();
  document.execCommand("copy");
  document.body.removeChild(ta);
  return Promise.resolve();
}

// Simple trial division test using BigInt (works for small numbers; can be slow for large)
function isPrimeTrialDivision(n) {
  if (n < 2n) return false;
  if (n === 2n || n === 3n) return true;
  if (n % 2n === 0n) return false;

  // i*i <= n
  for (let i = 3n; i * i <= n; i += 2n) {
    if (n % i === 0n) return false;
  }
  return true;
}

function setTestResult(text, kind) {
  const el = document.getElementById("testResult");
  el.classList.remove("good", "bad");
  if (kind) el.classList.add(kind);
  el.textContent = text;
}

function onTestClicked() {
  const input = document.getElementById("testInput").value.trim();

  // Allow underscores/spaces for readability
  const cleaned = input.replace(/[_\s]/g, "");
  if (!/^\d+$/.test(cleaned)) {
    setTestResult("Please enter a positive integer (digits only).", "bad");
    return;
  }

  let n;
  try {
    n = BigInt(cleaned);
  } catch {
    setTestResult("That number is too large to parse in this browser.", "bad");
    return;
  }

  // Keep expectations clear for students
  if (cleaned.length > 18) {
    setTestResult(
      "This demo uses trial division, which is slow for big numbers. Try a smaller value (<= 18 digits) or use the prime samples above.",
      "bad"
    );
    return;
  }

  const t0 = performance.now();
  const prime = isPrimeTrialDivision(n);
  const t1 = performance.now();

  if (prime) {
    setTestResult(`Result: PRIME (trial division). Time: ${(t1 - t0).toFixed(2)} ms`, "good");
  } else {
    setTestResult(`Result: COMPOSITE (trial division). Time: ${(t1 - t0).toFixed(2)} ms`, "bad");
  }
}

async function main() {
  const primeSelect = document.getElementById("primeSelect");
  const copyPrimeBtn = document.getElementById("copyPrimeBtn");

  let data;
  try {
    data = await loadPrimes();
  } catch (e) {
    document.getElementById("primeValue").textContent =
      "Could not load ./data/primes.json.\n\n" + String(e);
    return;
  }

  const samples = data.samples ?? [];
  if (!samples.length) {
    document.getElementById("primeValue").textContent =
      "No prime samples found in primes.json.";
    return;
  }

  // Populate dropdown
  for (const s of samples) {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = `${s.id} — ${s.label ?? ""}`.trim();
    primeSelect.appendChild(opt);
  }

  function getSelectedSample() {
    const id = primeSelect.value;
    return samples.find(s => s.id === id) ?? samples[0];
  }

  primeSelect.addEventListener("change", () => setPrimeUI(getSelectedSample()));
  setPrimeUI(getSelectedSample());

  copyPrimeBtn.addEventListener("click", async () => {
    const s = getSelectedSample();
    try {
      await copyTextToClipboard(s.prime);
      copyPrimeBtn.textContent = "Copied!";
      setTimeout(() => (copyPrimeBtn.textContent = "Copy"), 900);
    } catch {
      setTestResult("Copy failed (browser permission). You can select and copy manually.", "bad");
    }
  });

  document.getElementById("testBtn").addEventListener("click", onTestClicked);
  document.getElementById("testInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") onTestClicked();
  });

  // Show build info if present
  if (data.generated_at) {
    const meta = document.getElementById("primeMeta");
    meta.textContent = `${meta.textContent}   |   generated_at: ${data.generated_at}`;
  }
}

main();