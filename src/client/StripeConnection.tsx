import * as React from "react";
import { useEffect, useState } from "react";

type StripeInfo = {
  id: string;
  business_profile: {
    name: string;
  };
  country: string;
  default_currency: string;
};

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
      <h3>StripeConnection</h3>
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
