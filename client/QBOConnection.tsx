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
  companyInfo: QBOCompanyInfo;
  onDisconnect: () => void;
}) => {
  return (
    <ConnectionCard title="QuickBooks Online">
      {companyInfo ? (
        <div>
          <p>
            {companyInfo.CompanyName} ({companyInfo.Country})
          </p>
          <button
            className="mt-2 inline-block hover:bg-slate-100 text-red-500 font-bold py-2 px-4 rounded-full text-sm"
            onClick={() => {
              fetch("/qbo/disconnect").then(onDisconnect);
            }}
          >
            Disconnect
          </button>
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
