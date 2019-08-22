import {

    LOGIN_SUCCESS,
    LOGIN_FAILURE,
    LOGIN_CHECKED,

    LOGOUT_SESSION,

} from "./types";

const initialState = {
    validated: false,
    authenticated: false,
};

export default function (state=initialState, action) {

    if (action.type === LOGIN_CHECKED)
        return {...state, validated: true};

    if (action.type === LOGIN_FAILURE)
        return {...state, authenticated: false};

    if (action.type === LOGIN_SUCCESS) {
        localStorage.setItem("token", action.data.token);
        return {...state, authenticated: true};
    }

    if (action.type === LOGOUT_SESSION) {
        return initialState;
    }

    return state;
}
