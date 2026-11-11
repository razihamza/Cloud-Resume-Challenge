const API_URL = "https://4uwjlagcsh.execute-api.ap-south-2.amazonaws.com/visits";

async function updateCounter() {
  const el = document.getElementById("count");
  try {
    const response = await fetch(API_URL, { method: "POST" });
    if (!response.ok) throw new Error("HTTP " + response.status);
    const data = await response.json();
    el.textContent = data.visits;
  } catch (error) {
    console.error("Counter failed:", error);
    el.textContent = "unavailable";
  }
}

updateCounter();