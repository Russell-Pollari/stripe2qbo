import * as React from "react";
import { useEffect, useState } from "react";

import QBOConnection from "./components/QBOConnection";
import StripeConnection from "./components/StripeConnection";
import SyncSettings from "./components/settings/SyncSettings";
import Sync from "./components/Sync";
import type {
  QBOCompanyInfo,
  QBOAccount,
  QBOTaxCode,
  QBOVendor,
  Settings,
  StripeInfo,
} from "./types";

const App = () => {
  // TODO: useReducer or context manager for all this state!
  const [qboCompanyInfo, setQBoCompanyInfo] =
    React.useState<QBOCompanyInfo | null>(null);
  const [accounts, setAccounts] = useState<QBOAccount[]>([]);
  const [vendors, setVendors] = useState<QBOVendor[]>([]);
  const [taxCodes, setTaxCodes] = useState<QBOTaxCode[]>([]);
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [stripeInfo, setStripeInfo] = useState<StripeInfo | null>(null);

  useEffect(() => {
    fetch("/stripe/info")
      .then((response) => response.json())
      .then((data) => {
        setStripeInfo(data);
      });
  }, []);

  const loadAccount = async () => {
    const response = await fetch("/qbo/accounts");
    const data = await response.json();
    setAccounts(data);
  };

  const loadVendors = async () => {
    const response = await fetch("/qbo/vendors");
    const data = await response.json();
    setVendors(data);
  };

  const loadTaxCodes = async () => {
    const response = await fetch("/qbo/taxcodes");
    const data = await response.json();
    setTaxCodes(data);
  };

  const loadSettings = async () => {
    const response = await fetch("/settings");
    const data = await response.json();
    if (data) {
      setSettings(data);
    }
  };

  const loadCompanyInfo = async (): Promise<boolean> => {
    const response = await fetch("/qbo/info");
    const data = await response.json();
    if (data.CompanyName) {
      setQBoCompanyInfo(data);
      return true;
    } else {
      return false;
    }
  };

  useEffect(() => {
    setLoading(true);
    loadCompanyInfo()
      .then((isLoggedIn) => {
        if (isLoggedIn) {
          return Promise.all([
            loadAccount(),
            loadVendors(),
            loadTaxCodes(),
            loadSettings(),
          ]);
        }
      })
      .then(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between bg-green-300 p-4">
        <h1 className="font-semibold text-xl">Stripe 2 QBO</h1>
      </div>
      {loading ? (
        <div className="text-center p-10">Loading...</div>
      ) : (
        <div className="p-6">
          <div className="flex justify-around">
            <div className="basis-3/4">
              <Sync />
            </div>
            <div>
              <StripeConnection stripeInfo={stripeInfo} />
              <QBOConnection
                companyInfo={qboCompanyInfo}
                onDisconnect={() => setQBoCompanyInfo(null)}
              />
              <SyncSettings
                accounts={accounts}
                vendors={vendors}
                taxCodes={taxCodes}
                settings={settings}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
