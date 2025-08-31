// chat.js

async function chatWithBot(userInput, threadId = "default") {
  try {
    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        user_input: userInput,
        thread_id: threadId
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();

    console.log("Bot Response:", data.response);

    return data.response;
  } catch (error) {
    console.error("Error calling chatbot API:", error);
  }
}

// Example usage
chatWithBot("what is the capital of India", "session123");
