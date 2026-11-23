//////.    MADE BY AI ///////////




// Keep each RTI request in its portal tab while the user logs in.
async function handleRequest(message, sender) {
  if (!sender.tab || !sender.url) throw Error("A portal tab is required.");
  const url = new URL(sender.url);
  if (url.origin !== "https://onlinerti.gujarat.gov.in" ||
      (url.pathname !== "/rti_portal" && !url.pathname.startsWith("/rti_portal/"))) {
    throw Error("Open the Gujarat RTI portal.");
  }
  const key = "rti_" + sender.tab.id;

  if (message.type === "SAVE_RTI") {
    const data = message.data;
    if (!data || !/^[a-f0-9-]{36}$/.test(data.id) || typeof data.text !== "string" ||
        !data.text.trim() || data.text.length > 750) throw Error("RTI text must contain 1 to 750 characters.");
    await chrome.storage.session.set({[key]: data});
    return {message: "RTI text saved for login."};
  }
  if (message.type === "GET_RTI") {
    const saved = await chrome.storage.session.get(key);
    return saved[key] || null;
  }
  if (message.type === "FILLED_RTI") {
    await chrome.storage.session.remove(key);
    return {message: "RTI text filled."};
  }
  throw Error("Reload the OpenCity RTI extension and portal page.");
}

chrome.runtime.onMessage.addListener((message, sender, respond) => {
  handleRequest(message, sender).then(respond).catch(error => respond({error: error.message}));
  return true;
});

chrome.tabs.onRemoved.addListener(tabId => {
  chrome.storage.session.remove("rti_" + tabId);
});
