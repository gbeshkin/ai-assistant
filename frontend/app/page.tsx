import ChatBox from "@/components/ChatBox";

export default function Home() {
  return (
    <main className="page-shell">
      <section className="hero">
        <div className="hero-badge">Tallinn AI Assistant · Railway V3</div>
        <h1>Демо ассистент города Таллинна</h1>
        <p className="hero-text">
          Задай вопрос текстом или голосом. Демо поддерживает русский, eesti keel и English.
        </p>
      </section>

      <ChatBox />
    </main>
  );
}
