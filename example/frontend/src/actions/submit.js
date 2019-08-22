import axios from "axios";
import config from "../config";

import {
    LOGIN_CHECKED,
    GENERAL_FAILURE,

    SET_REGISTER_CONTEXT,
    CLR_REGISTER_REDUCER,


} from "../reducers/types";


export const submit_registration = (index, content) => dispatch => {

    const session = localStorage.getItem("token");
    const headers = {authorization: `Token ${session}`};

    axios.post(config.locate(`/multi-factor/register/${index}/`), content, {headers})
        .then(response => {
            dispatch({type: SET_REGISTER_CONTEXT, data: response.data});


        })
        .catch(response => {
            dispatch({type: GENERAL_FAILURE, data: response.data});
        })
};


export const submit_validation = (index, value, refresh) => dispatch => {
    const session = localStorage.getItem("token");
    const headers = {authorization: `Token ${session}`};

    axios.post(config.locate(`/multi-factor/${index}/`), {value}, {headers})
        .then(response => {

            dispatch({type: LOGIN_CHECKED,        data: null});
            dispatch({type: CLR_REGISTER_REDUCER, data: null});

        })
        .catch(response => {
            dispatch({type: GENERAL_FAILURE, data: response.data});
        })
};
