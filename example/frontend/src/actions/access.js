import axios from "axios";
import config from "../config";

import {

    ACCESS_DENIED,
    ACCESS_GRANTED,

} from "../reducers/types";


export const request_access = () => dispatch => {

    const session = localStorage.getItem("token");
    const headers = {authorization: `Token ${session}`};
    
    axios.get(config.locate("/access/"), {headers})
        .then(response => {
            dispatch({type: ACCESS_GRANTED, data: response.data})
        })
        .catch(response => {
            dispatch({type: ACCESS_DENIED, data: response.data})
        })
};
