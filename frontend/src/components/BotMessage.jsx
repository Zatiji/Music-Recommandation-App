import "../styles/Messages.css";
import reactLogo from "../assets/react.svg";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";

// Fix common streaming glitches: unclosed ``` fences
function stabilizeMarkdown(md) {
  const fenceCount = (md.match(/```/g) || []).length;
  if (fenceCount % 2 === 1) md += "\n```";
  return md;
}

// If the server accidentally sends escaped sequences like "\\n",
// decode them into real newlines so Markdown can render them.
function decodeEscapes(md) {
  return md.replace(/\\n/g, "\n").replace(/\\t/g, "\t");
}

function BotMessage({ text }) {
  const raw = text || "";
  const decoded = decodeEscapes(raw);
  const display = stabilizeMarkdown(decoded);

  return (
    <>
      <div className="bot-message">
        <ReactMarkdown
          remarkPlugins={[remarkGfm, remarkBreaks]}
          components={{
            a: ({node, ...props}) => (
              <a {...props} target="_blank" rel="noopener noreferrer" />
            ),
          }}
        >
          {display}
        </ReactMarkdown>
      </div>
      <div className="image-in-bot-message">
        <img
          src={reactLogo}
          alt="image-in-bot-message"
          className="image-in-bot-message"
        />
      </div>
    </>
  );
}

export default BotMessage;