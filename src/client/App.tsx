import * as React from "react";

import QBOConnection from "./QBOConnection";
import StripeConnection from "./StripeConnection";
import SyncSettings from "./SyncSettings";

const App = () => {
  return (
    <div>
      <h1>Stripe 2 QBO</h1>
      <StripeConnection />
      <QBOConnection />
      <SyncSettings />
    </div>
  );
};

export default App;
