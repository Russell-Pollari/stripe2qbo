import * as React from "react";

import type { StripeInfo } from "../types";
import ConnectionCard from "./ConnectionCard";

const connect = () => {
  fetch("/stripe/oauth2")
    .then((response) => response.json())
    .then((data: string) => {
      location.href = data;
    });
};

const StripeConnection = ({
  stripeInfo,
  onDisconnect,
}: {
  stripeInfo: StripeInfo | null;
  onDisconnect: () => void;
}) => {
  return (
    <ConnectionCard
      isConnected={!!stripeInfo}
      title="Stripe account"
      disconnect={() => fetch("/stripe/disconnect").then(onDisconnect)}
    >
      {stripeInfo ? (
        <span>
          {stripeInfo.business_profile.name || stripeInfo.id} (
          {stripeInfo.country})
        </span>
      ) : (
        <button
          className="inline-block hover:bg-slate-100 text-gray-500 font-bold p-2 rounded-full text-sm"
          onClick={connect}
        >
          Connect a Stripe account
        </button>
      )}
    </ConnectionCard>
  );
};

export default StripeConnection;
