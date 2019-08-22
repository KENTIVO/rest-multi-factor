import history from "../history";

import { connectRouter } from "connected-react-router";
import { combineReducers } from "redux";


import login from "./login";
import access from "./access";

import register from "./register";
import validate from "./validate";


export default combineReducers({
    login,
    access,
    register,
    validate,

    router: connectRouter(history),
})
