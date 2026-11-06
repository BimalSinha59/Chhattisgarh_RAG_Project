
import React, { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { checkBackend, sendChatMessage } from "./api";
import "./App.css";

const LANGUAGES = [
  { value: "hi", label: "हिन्दी" },
  { value: "en", label: "English" },
  { value: "hne", label: "छत्तीसगढ़ी" },
];

const VOICE_LANGUAGES = [
  { value: "hi-IN", label: "Hindi voice" },
  { value: "en-IN", label: "English voice" },
];

const SUGGESTIONS = [
  "बस्तर दशहरा की परंपराएँ बताइए",
  "Tell me about Chhattisgarh's history",
  "छत्तीसगढ़ के प्रमुख लोकनृत्य कौन से हैं?",
  "What are the famous places in Bastar?",
];

function getAnswer(data) {
  const answer =
    data?.answer ?? data?.response ?? data?.message ?? data?.result;

  if (typeof answer === "string") return answer;
  if (answer != null) return JSON.stringify(answer, null, 2);

  return "Backend se response mila, lekin answer field nahi mili. Backend response schema check karein.";
}

/*
 * Clean escaped Markdown and common HTML line-break artifacts.
 * Keep real Markdown table row boundaries intact.
 */
function cleanMarkdown(text) {
  if (typeof text !== "string") return "";

  let cleaned = text
    .replace(/\r\n?/g, "\n")
    // Convert escaped Markdown punctuation to actual Markdown.
    .replace(/\\([*_~`|])/g, "$1")
    // Remove escaping before HTML break tags.
    .replace(/\\(<br\s*\/?>)/gi, "$1")
    .trim();

  /*
   * If the backend has put an entire Markdown table on one line
   * and used <br> between rows, restore those row boundaries.
   */
  if (/<br\s*\/?>/i.test(cleaned) && cleaned.includes("|")) {
    cleaned = cleaned
      .replace(/^\s*<br\s*\/?>\s*/i, "")
      .replace(/\s*<br\s*\/?>\s*$/i, "")
      .replace(/\s*<br\s*\/?>\s*/gi, "\n");
  } else {
    cleaned = cleaned.replace(/<br\s*\/?>/gi, "\n");
  }

  return cleaned.trim();
}

function getSourceLabel(source, index) {
  return (
    source?.title ||
    source?.name ||
    source?.document_title ||
    source?.source ||
    `Source ${index + 1}`
  );
}

function getSourceDetail(source) {
  return (
    source?.url ||
    source?.source_url ||
    source?.path ||
    source?.file ||
    source?.document ||
    ""
  );
}

function getSpeechLanguage(language) {
  if (language === "en") return "en-IN";
  return "hi-IN";
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [language, setLanguage] = useState("hi");
  const [voiceLanguage, setVoiceLanguage] = useState("hi-IN");

  const [loading, setLoading] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);
  const [error, setError] = useState("");
  const [checkingBackend, setCheckingBackend] = useState(true);

  const [isListening, setIsListening] = useState(false);
  const [listeningError, setListeningError] = useState("");
  const [speakingIndex, setSpeakingIndex] = useState(null);

  const bottomRef = useRef(null);
  const inputRef = useRef(null);
  const recognitionRef = useRef(null);
  const shouldListenRef = useRef(false);

  useEffect(() => {
    let active = true;

    checkBackend()
      .then((data) => {
        if (active) setBackendOnline(data?.status === "ok");
      })
      .catch(() => {
        if (active) setBackendOnline(false);
      })
      .finally(() => {
        if (active) setCheckingBackend(false);
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    return () => {
      shouldListenRef.current = false;

      if (recognitionRef.current) {
        recognitionRef.current.onresult = null;
        recognitionRef.current.onerror = null;
        recognitionRef.current.onend = null;

        try {
          recognitionRef.current.stop();
        } catch {
          // Recognition may already have stopped.
        }
      }

      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  function stopListening() {
    shouldListenRef.current = false;

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        // Recognition may already have stopped.
      }
    }

    setIsListening(false);
  }

  function startListening() {
    setListeningError("");
    setError("");

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setListeningError(
        "Voice input supported nahi hai. Chrome ya Edge ke latest version mein try karein."
      );
      return;
    }

    if (loading) return;

    if (shouldListenRef.current) {
      stopListening();
      return;
    }

    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      setSpeakingIndex(null);
    }

    const recognition = new SpeechRecognition();

    // Voice-input language is controlled by its own selector.
    recognition.lang = voiceLanguage;
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognitionRef.current = recognition;
    shouldListenRef.current = true;
    setIsListening(true);

    recognition.onresult = (event) => {
      let transcript = "";
      let finalTranscript = "";

      for (let i = 0; i < event.results.length; i += 1) {
        const result = event.results[i];
        const recognizedText = result[0]?.transcript || "";

        transcript += recognizedText;

        if (result.isFinal) {
          finalTranscript += recognizedText;
        }
      }

      setQuestion(transcript.trim());

      if (finalTranscript.trim()) {
        setLanguage(voiceLanguage === "en-IN" ? "en" : "hi");
      }
    };

    recognition.onerror = (event) => {
      shouldListenRef.current = false;
      setIsListening(false);

      if (
        event.error === "not-allowed" ||
        event.error === "service-not-allowed"
      ) {
        setListeningError(
          "Microphone permission nahi mili. Browser settings mein microphone allow karein."
        );
      } else if (event.error === "no-speech") {
        setListeningError(
          "Awaaz detect nahi hui. Mic dabakar dobara boliye."
        );
      } else if (event.error === "language-not-supported") {
        setListeningError(
          "Selected voice language browser mein supported nahi hai. Hindi ya English select karke try karein."
        );
      } else if (event.error !== "aborted") {
        setListeningError(
          "Voice input start nahi ho paya. Microphone aur browser support check karein."
        );
      }
    };

    recognition.onend = () => {
      shouldListenRef.current = false;
      setIsListening(false);
      inputRef.current?.focus();
    };

    try {
      recognition.start();
    } catch {
      shouldListenRef.current = false;
      setIsListening(false);
      setListeningError(
        "Mic start nahi ho paya. Kuch seconds baad dobara try karein."
      );
    }
  }

  function speakAnswer(text, index) {
    if (!("speechSynthesis" in window)) {
      setListeningError(
        "Voice output is browser mein supported nahi hai. Chrome ya Edge mein try karein."
      );
      return;
    }

    if (speakingIndex === index) {
      window.speechSynthesis.cancel();
      setSpeakingIndex(null);
      return;
    }

    window.speechSynthesis.cancel();
    setSpeakingIndex(null);

    // Speak readable text rather than Markdown punctuation.
    const readableText = cleanMarkdown(text)
      .replace(/!\[([^\]]*)\]\([^)]+\)/g, "$1")
      .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
      .replace(/^\s{0,3}#{1,6}\s+/gm, "")
      .replace(/^\s*[-*+]\s+/gm, "")
      .replace(/^\s*\d+\.\s+/gm, "")
      .replace(/[*_~`]/g, "")
      .replace(/\|/g, " ")
      .replace(/---+/g, " ");

    const utterance = new SpeechSynthesisUtterance(readableText);
    const speechLanguage = getSpeechLanguage(language);

    utterance.lang = speechLanguage;
    utterance.rate = 1;
    utterance.pitch = 1;

    const voices = window.speechSynthesis.getVoices();

    const preferredVoice =
      voices.find(
        (voice) =>
          voice.lang.toLowerCase() === speechLanguage.toLowerCase()
      ) ||
      voices.find((voice) =>
        voice.lang
          .toLowerCase()
          .startsWith(language === "en" ? "en" : "hi")
      );

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.onstart = () => setSpeakingIndex(index);

    utterance.onend = () => {
      setSpeakingIndex(null);
    };

    utterance.onerror = () => {
      setSpeakingIndex(null);
      setListeningError(
        "Voice playback nahi ho paya. Browser mein required language voice available hai ya nahi, check karein."
      );
    };

    window.speechSynthesis.speak(utterance);
  }

  function stopSpeaking() {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }

    setSpeakingIndex(null);
  }

  async function handleSend(event, suggestedQuestion) {
    event?.preventDefault();

    const text = (suggestedQuestion ?? question).trim();

    if (!text || loading) return;

    stopListening();
    stopSpeaking();

    setListeningError("");
    setError("");

    setMessages((previous) => [
      ...previous,
      { role: "user", content: text },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const data = await sendChatMessage(text, language);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: getAnswer(data),
          sources: Array.isArray(data?.sources) ? data.sources : [],
          generationMode: data?.generation_mode,
          responseLanguage: language,
        },
      ]);

      setBackendOnline(true);
    } catch (err) {
      setError(
        err?.message ||
          "Backend se connect nahi ho paya. Check karein ki FastAPI server chal raha hai."
      );

      setBackendOnline(false);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function startNewChat() {
    if (loading) return;

    stopListening();
    stopSpeaking();

    setMessages([]);
    setQuestion("");
    setError("");
    setListeningError("");

    inputRef.current?.focus();
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">मोर</div>
          <div className="brand-copy">
            <strong>Mor Chhattisgarh</strong>
            <span>Multilingual AI Assistant</span>
          </div>
        </div>

        <button
          type="button"
          className="new-chat"
          onClick={startNewChat}
          disabled={loading}
        >
          <span className="new-chat-icon">＋</span>
          New chat
        </button>

        <div className="sidebar-section">
          <p className="sidebar-label">EXPLORE CHHATTISGARH</p>
          <div className="sidebar-topic">
            <span>◈</span> History and heritage
          </div>
          <div className="sidebar-topic">
            <span>✳</span> Culture and festivals
          </div>
          <div className="sidebar-topic">
            <span>⌖</span> District information
          </div>
          <div className="sidebar-topic">
            <span>♫</span> Folk art and language
          </div>
        </div>

        <div className="sidebar-info">
          <div className="info-icon">i</div>
          <p>
            Answers are generated using your Chhattisgarh knowledge base and
            AI model.
          </p>
        </div>

        <div className="sidebar-footer">
          <span className={`status-dot ${backendOnline ? "online" : ""}`} />
          <span>
            {checkingBackend
              ? "Checking backend..."
              : backendOnline
                ? "Backend connected"
                : "Backend unavailable"}
          </span>
        </div>
      </aside>

      <main className="chat-panel">
        <header className="topbar">
          <div className="mobile-brand">
            <div className="brand-icon small">मोर</div>
            <div>
              <strong>Mor Chhattisgarh AI</strong>
              <span>Knowledge assistant</span>
            </div>
          </div>

          <div className="desktop-heading">
            <strong>Mor Chhattisgarh AI</strong>
            <span>Explore the land of culture and heritage</span>
          </div>

          <label className="language-control">
            <span>Response language</span>
            <select
              value={language}
              onChange={(event) => {
                setLanguage(event.target.value);
                setListeningError("");
              }}
              disabled={loading || isListening}
              aria-label="Choose response language"
            >
              {LANGUAGES.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
        </header>

        <section
          className={`conversation ${
            messages.length === 0 ? "conversation-empty" : ""
          }`}
        >
          {messages.length === 0 ? (
            <div className="welcome">
              <div className="welcome-symbol">
                <span>✳</span>
              </div>

              <p className="eyebrow">JAI JOHAR · राम राम · जय जोहार</p>

              <h1>
                Your Chhattisgarh.
                <br />
                <span>Your knowledge.</span>
              </h1>

              <p className="welcome-description">
                Discover Chhattisgarh's history, traditions, districts and
                culture. Ask your question in Hindi, English or Chhattisgarhi.
              </p>

              <div className="suggestion-heading">
                <span>GET STARTED</span>
                <span>Try asking</span>
              </div>

              <div className="suggestions">
                {SUGGESTIONS.map((item) => (
                  <button
                    type="button"
                    key={item}
                    onClick={() => handleSend(undefined, item)}
                    disabled={loading}
                  >
                    <span>{item}</span>
                    <span className="suggestion-arrow">↗</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map((message, index) => (
                <article
                  className={`message ${message.role}`}
                  key={`${message.role}-${index}`}
                >
                  <div className="avatar">
                    {message.role === "user" ? (
                      <span>YOU</span>
                    ) : (
                      <span>मोर</span>
                    )}
                  </div>

                  <div className="message-body">
                    <div className="message-header">
                      <span className="message-label">
                        {message.role === "user" ? "You" : "Mor Chhattisgarh"}
                      </span>

                      {message.role === "assistant" &&
                        message.generationMode && (
                          <span className="generation-tag">
                            {message.generationMode === "groq"
                              ? "Groq AI"
                              : message.generationMode}
                          </span>
                        )}
                    </div>

                    <div className="message-content markdown-content">
                      {message.role === "user" ? (
                        message.content
                      ) : (
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          skipHtml
                        >
                          {cleanMarkdown(message.content)}
                        </ReactMarkdown>
                      )}
                    </div>

                    {message.role === "assistant" && (
                      <div className="voice-controls">
                        <button
                          type="button"
                          className="voice-button"
                          onClick={() => speakAnswer(message.content, index)}
                          aria-label={
                            speakingIndex === index
                              ? "Stop speaking"
                              : "Listen to answer"
                          }
                          title={
                            speakingIndex === index
                              ? "Stop voice output"
                              : "Listen to answer"
                          }
                        >
                          {speakingIndex === index ? "⏹ Stop" : "🔊 Listen"}
                        </button>
                      </div>
                    )}

                    {message.role === "assistant" &&
                      Array.isArray(message.sources) &&
                      message.sources.length > 0 && (
                        <details className="sources">
                          <summary>
                            <span className="source-symbol">▤</span>
                            Sources ({message.sources.length})
                          </summary>

                          <div className="source-list">
                            {message.sources.map((source, sourceIndex) => {
                              const label = getSourceLabel(
                                source,
                                sourceIndex
                              );
                              const detail = getSourceDetail(source);

                              return (
                                <div
                                  className="source-item"
                                  key={`${label}-${sourceIndex}`}
                                >
                                  <div className="source-number">
                                    {sourceIndex + 1}
                                  </div>
                                  <div className="source-copy">
                                    <strong>{label}</strong>
                                    {detail && <span>{detail}</span>}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </details>
                      )}
                  </div>
                </article>
              ))}

              {loading && (
                <div className="message assistant">
                  <div className="avatar">
                    <span>मोर</span>
                  </div>
                  <div className="message-body">
                    <div className="message-label">Mor Chhattisgarh</div>
                    <div className="typing">
                      <span />
                      <span />
                      <span />
                      <p>Searching knowledge base and generating answer...</p>
                    </div>
                  </div>
                </div>
              )}

              <div ref={bottomRef} />
            </div>
          )}
        </section>

        {(error || listeningError) && (
          <div className="error-banner" role="alert">
            <span>⚠</span>
            <div>
              <strong>
                {listeningError
                  ? "Voice feature notice"
                  : "Unable to get an answer"}
              </strong>

              {error && <p>{error}</p>}
              {listeningError && <p>{listeningError}</p>}

              <button
                type="button"
                onClick={() => {
                  setError("");
                  setListeningError("");
                  inputRef.current?.focus();
                }}
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        <div className="composer-wrap">
          <form className="composer" onSubmit={(event) => handleSend(event)}>
            <textarea
              ref={inputRef}
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (
                  event.key === "Enter" &&
                  !event.shiftKey &&
                  !event.nativeEvent.isComposing
                ) {
                  event.preventDefault();
                  handleSend(event);
                }
              }}
              placeholder={
                isListening
                  ? "Listening... ab boliye"
                  : "Ask anything about Chhattisgarh..."
              }
              rows={1}
              disabled={loading}
              aria-label="Enter your question"
            />

            <select
              className="voice-language-select"
              value={voiceLanguage}
              onChange={(event) => setVoiceLanguage(event.target.value)}
              disabled={loading || isListening}
              aria-label="Voice input language"
              title="Choose the language you will speak"
            >
              {VOICE_LANGUAGES.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>

            <button
              className={`mic-button ${isListening ? "mic-active" : ""}`}
              type="button"
              onClick={startListening}
              disabled={loading}
              aria-label={isListening ? "Stop voice input" : "Start voice input"}
              title={isListening ? "Stop listening" : "Speak your question"}
            >
              {isListening ? "⏹" : "🎙️"}
            </button>

            <button
              className="send-button"
              type="submit"
              disabled={loading || !question.trim()}
              aria-label="Send message"
              title="Send message"
            >
              {loading ? (
                <span className="send-loading">…</span>
              ) : (
                <span>↑</span>
              )}
            </button>
          </form>

          <div className="composer-meta">
            <span>
              <span className="composer-lock">◇</span>
              Powered by hybrid search · HNSW + BM25
            </span>
            <span>AI responses may contain errors</span>
          </div>
        </div>
      </main>
    </div>
  );
}
