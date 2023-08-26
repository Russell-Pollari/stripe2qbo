import * as React from "react";
import { useEffect, useState } from "react";

import type { StripeInfo } from "./types";

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
    <div>
      <h3>Stripe Connection</h3>
      {stripeInfo && (
        <div>
          <p>Company Name: {stripeInfo.business_profile.name}</p>
          <p>Country: {stripeInfo.country}</p>
          <p>Currency: {stripeInfo.default_currency}</p>
        </div>
      )}
    </div>
  );
};

export default StripeConnection;
