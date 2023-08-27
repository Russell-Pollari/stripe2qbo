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
    <ConnectionCard title="Stripe account">
      {stripeInfo && (
        <span>
          {stripeInfo.business_profile.name} ({stripeInfo.country})
        </span>
      )}
    </ConnectionCard>
  );
};

export default StripeConnection;
