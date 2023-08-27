import * as React from "react";
import { useEffect, useState } from "react";

import type { StripeInfo } from "./types";
import ConnectionCard from "./ConnectionCard";

const StripeConnection = () => {
  const [stripeInfo, setStripeInfo] = useState<StripeInfo | null>(null);

  useEffect(() => {
    fetch("/stripe/info")
      .then((response) => response.json())
      .then((data) => {
        setStripeInfo(data);
      });
  }, []);

  return (
    <ConnectionCard title="Stripe">
      {stripeInfo && (
        <table className="table-auto">
          <tbody>
            <tr>
              <td className="font-semibold mr-4">Company:</td>
              <td>{stripeInfo.business_profile.name}</td>
            </tr>
            <tr>
              <td className="font-semibold mr-4">Country:</td>
              <td>{stripeInfo.country}</td>
            </tr>
            <tr>
              <td className="font-semibold mr-4">Currency:</td>
              <td>{stripeInfo.default_currency.toUpperCase()}</td>
            </tr>
          </tbody>
        </table>
      )}
    </ConnectionCard>
  );
};

export default StripeConnection;
