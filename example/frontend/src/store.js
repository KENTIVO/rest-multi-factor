import thunk from 'redux-thunk'

import { routerMiddleware } from "connected-react-router";
import { composeWithDevTools } from "redux-devtools-extension";
import { applyMiddleware, createStore } from "redux";

import history from "./history";
import reducer from "./reducers/index";

const middleware = composeWithDevTools(applyMiddleware(
    thunk, routerMiddleware(history)
));

export default createStore(reducer, {}, middleware);
