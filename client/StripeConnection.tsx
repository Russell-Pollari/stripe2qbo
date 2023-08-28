import * as React from "react";

import type { StripeInfo } from "./types";
import ConnectionCard from "./ConnectionCard";

const StripeConnection = ({
  stripeInfo,
}: {
  stripeInfo: StripeInfo | null;
}) => {
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
