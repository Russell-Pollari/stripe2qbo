import * as React from "react";

import QBOConnection from "./QBOConnection";
import StripeConnection from "./StripeConnection";

const App = () => {
  return (
    <div>
      <h1>Stripe 2 QBO</h1>
      <StripeConnection />
      <QBOConnection />
    </div>
  );
};

export default App;
