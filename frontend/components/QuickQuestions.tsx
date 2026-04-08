type Props = {
  onPick: (question: string) => void;
};

const questions = [
  "Как оформить парковочное разрешение в Таллинне?",
  "Куда пожаловаться на яму во дворе?",
  "How can I find Tallinn city services online?",
  "Kuidas leida Tallinna linnateenuseid internetis?",
  "What should I do with bulky waste?",
  "Как узнать про общественный транспорт?"
];

export default function QuickQuestions({ onPick }: Props) {
  return (
    <div>
      <p className="panel-title">Try one of these demo questions:</p>
      <div className="quick-grid">
        {questions.map((question) => (
          <button
            key={question}
            type="button"
            className="quick-button"
            onClick={() => onPick(question)}
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
