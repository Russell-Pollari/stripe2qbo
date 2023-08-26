import * as React from "react";

import QBOConnection from "./QBOConnection";
import StripeConnection from "./StripeConnection";
import SyncSettings from "./settings/SyncSettings";

const App = () => {
  const [qboConnected, setQBOConnected] = React.useState(false);

  React.useEffect(() => {
    fetch("/qbo/info")
      .then((res) => res.json())
      .then((data) => {
        if (data.CompanyName) {
          setQBOConnected(true);
        }
      });
  }, []);

  return (
    <div>
      <h1>Stripe 2 QBO</h1>
      <StripeConnection />
      <div>
        <button
          onClick={() => {
            fetch("/sync")
              .then((res) => res.json())
              .then((data) => {
                console.log(data);
              });
          }}
        >
          SYNC!!
        </button>
      </div>
      <QBOConnection />
      {qboConnected && <SyncSettings />}
    </div>
  );
};

export default App;
