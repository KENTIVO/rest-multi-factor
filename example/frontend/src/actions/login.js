import axios from "axios";
import config from "../config";

import { LOGIN_SUCCESS, LOGIN_FAILURE, LOGOUT_SESSION } from "../reducers/types.js"

/**
 * Authenticate the user with HTTP basic auth.
 *
 * @param {string} username: The username to submit
 *
 * @param {string} password: The password to submit
 */
export const login = (username, password) => dispatch => {
    const content = null;
    const request = {auth: {username, password}};

    axios.post(config.locate("/login/"), content, request)
        .then(response => {
            dispatch({type: LOGIN_SUCCESS, data: {"token": response.data.token}})
        })
        .catch(response => {
            dispatch({type: LOGIN_FAILURE, data: {"token": null}})
        })
};


export const logout = () => ({type: LOGOUT_SESSION, data: null});
