(() => {
  const originalFetch = window.fetch.bind(window);
  window.fetch = (input, init) => {
    if (typeof input === "string" && input.startsWith("/api/")) {
      input = "/rostering" + input;
    }
    return originalFetch(input, init);
  };
  if (typeof loadExample === "function") {
    loadExample();
  }
})();
