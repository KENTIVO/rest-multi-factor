import axios from "axios";
import config from  "../config";

import {

    GENERAL_FAILURE,

    SET_REGISTER_DEVICES,
    SET_VALIDATE_DEVICES,

} from "../reducers/types";


export const get_all_devices = () => dispatch => {

    const session = localStorage.getItem("token");
    const headers = {authorization: `Token ${session}`};

    axios.get(config.locate("/multi-factor/register/"), {headers})
        .then(response => {
            dispatch({type: SET_REGISTER_DEVICES, data: response.data})
        })
        .catch(response => {
            dispatch({type: GENERAL_FAILURE, data: response})
        })
};


export const get_usr_devices = () => dispatch => {

    const session = localStorage.getItem("token");
    const headers = {authorization: `Token ${session}`};

    axios.get(config.locate("/multi-factor/"), {headers})
        .then(response => {
            dispatch({type: SET_VALIDATE_DEVICES, data: response.data})
        })
        .catch(response => {
            dispatch({type: GENERAL_FAILURE, data: response})
        })
};
