import * as React from "react";

import type { QBOCompanyInfo } from "./types";
import ConnectionCard from "./ConnectionCard";

const connect = () => {
  fetch("/qbo/oauth2")
    .then((response) => response.json())
    .then((data: string) => {
      location.href = data;
    });
};

const QBOConnection = ({
  companyInfo,
  onDisconnect,
}: {
  companyInfo?: QBOCompanyInfo;
  onDisconnect: () => void;
}) => {
  const disconnect = () => {
    fetch("/qbo/disconnect").then(onDisconnect);
  };

  return (
    <ConnectionCard
      title="QuickBooks Online"
      isConnected={!!companyInfo}
      disconnect={disconnect}
    >
      {companyInfo ? (
        <div>
          {companyInfo.CompanyName} ({companyInfo.Country})
        </div>
      ) : (
        <button
          className="inline-block hover:bg-slate-100 text-gray-500 font-bold p-2 rounded-full text-sm"
          onClick={connect}
        >
          Connect a QBO account
        </button>
      )}
    </ConnectionCard>
  );
};

export default QBOConnection;
