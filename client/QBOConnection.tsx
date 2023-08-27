import * as React from "react";
import { useEffect, useState } from "react";

import type { QBOCompanyInfo } from "./types";
import ConnectionCard from "./ConnectionCard";

const connect = () => {
  fetch("/qbo/oauth2")
    .then((response) => response.json())
    .then((data: string) => {
      location.href = data;
    });
};

const QBOConnection = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [companyInfo, setCompanyInfo] = useState<QBOCompanyInfo | null>(null);

  useEffect(() => {
    fetch("/qbo/info")
      .then((response) => response.json())
      .then((data) => {
        if (data.CompanyName) {
          setCompanyInfo(data);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return (
    <ConnectionCard title="QuickBooks Online">
      {loading && <p>Loading...</p>}
      {companyInfo ? (
        <div>
          <p>Company Name: {companyInfo.CompanyName}</p>
          <p>Country: {companyInfo.Country}</p>
          <button
            onClick={() => {
              fetch("/qbo/disconnect").then(() => setCompanyInfo(null));
            }}
          >
            Disconnect
          </button>
        </div>
      ) : (
        <button onClick={connect}>Connect a QBO account</button>
      )}
    </ConnectionCard>
  );
};

export default QBOConnection;
