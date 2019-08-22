import axios from "axios";
import config from "../config";

import {
    GENERAL_FAILURE,

    SET_REGISTER_CURRENT,
    SET_REGISTER_OPTIONS,
    SET_VERIFIER_OPTIONS,

} from "../reducers/types";


export const select_register = index => dispatch => {
    const session = localStorage.getItem("token");
    const headers = {authorization: `Token ${session}`};

    axios.options(config.locate(`/multi-factor/register/${index}/`), {headers})
        .then(response => {
            dispatch({type: SET_REGISTER_OPTIONS, data: response.data});
            dispatch({type: SET_REGISTER_CURRENT, data: index});
        })
        .catch(response => {
            dispatch({type: GENERAL_FAILURE, data: response.data})
        })

};


export const select_verify = index => dispatch => {
    const session = localStorage.getItem("token");
    const headers = {authorization: `Token ${session}`};

    axios.options(config.locate(`/multi-factor/register/${index}/`), {headers})
        .then(response => {
            dispatch({type: SET_VERIFIER_OPTIONS, data: response.data});


        })
        .catch(response => {
            dispatch({type: GENERAL_FAILURE, data: response.data})
        })
};
