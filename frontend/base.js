(() => {
  const originalFetch = window.fetch.bind(window);
  window.fetch = (input, init) => {
    if (typeof input === "string" && input.startsWith("/api/")) {
      input = "/rostering" + input;
    }
    return originalFetch(input, init);
  };
  const docsLink = document.querySelector("footer a");
  if (docsLink) docsLink.href = "/rostering/docs";
  if (typeof loadExample === "function") {
    loadExample();
  }
})();
