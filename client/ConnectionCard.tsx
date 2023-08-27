import * as React from "react";

const ConnectionCard = ({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) => (
  <div className="shadow-lg p-4 mb-2">
    <h3 className="font-semibold mb-2">{title}</h3>
    {children}
  </div>
);

export default ConnectionCard;
