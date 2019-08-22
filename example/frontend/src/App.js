import React from "react";

import { Provider } from "react-redux";
import { Switch, Route } from "react-router-dom";
import { ConnectedRouter } from 'connected-react-router'

import store from './store'
import history from "./history";

import Login from "./components/Login";
import Access from "./components/Access";
import Validate from "./components/Validate";

import Device from "./components/Register/Device";
import Context from "./components/Register/Context";
import Register from "./components/Register/Register";


function App() {
    return (
        <Provider store={store}>
            <ConnectedRouter history={history}>
                <Switch>
                    <Route exact component={Access} path="/"/>
                    <Route exact component={Login} path="/login/"/>

                    <Route exact component={Validate} path="/validate/"/>
                    <Route exact component={Register} path="/register/"/>
                    <Route exact component={Context}  path="/register/context/"/>
                    <Route exact component={Device}   path="/register/device/"/>

                    <Route component={() => "Not found"}/>

                    {/*<Route component={<Redirect to={"/login/"} />} />*/}
                </Switch>
            </ConnectedRouter>
        </Provider>
    );
}

export default App;
