import * as React from "react";

const ConnectionCard = ({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) => (
  <div className="shadow-lg w-25 p-6">
    <h3 className="font-semibold border-b-2 border-gray-600 mb-2">{title}</h3>
    {children}
  </div>
);

export default ConnectionCard;
