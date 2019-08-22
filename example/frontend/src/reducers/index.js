import history from "../history";

import { connectRouter } from "connected-react-router";
import { combineReducers } from "redux";


import login from "./login";
import access from "./access";
import verify from "./verify";
import register from "./register";


export default combineReducers({
    login,
    access,
    verify,
    register,

    router: connectRouter(history),
})
