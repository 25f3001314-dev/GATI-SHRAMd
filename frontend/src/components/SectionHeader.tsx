type SectionHeaderProps = {
  eyebrow?: string;
  title: string;
  detail?: string;
};

export function SectionHeader({ eyebrow, title, detail }: SectionHeaderProps) {
  return (
    <div className="section-header">
      <div>
        {eyebrow ? <div className="eyebrow">{eyebrow}</div> : null}
        <h2>{title}</h2>
      </div>
      {detail ? <span className="section-kicker">{detail}</span> : null}
    </div>
  );
}
