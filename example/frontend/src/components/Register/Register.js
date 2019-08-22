import React from "react";
import PropTypes from "prop-types";

import { connect } from "react-redux";

import { select_register } from "../../actions/select";
import { get_all_devices } from "../../actions/devices";


class Register extends React.Component {
    static propTypes = {
        current: PropTypes.number,
        devices: PropTypes.arrayOf(PropTypes.object).isRequired,

        select_register: PropTypes.func.isRequired,
        get_all_devices: PropTypes.func.isRequired,
    };

    constructor(props) {
        super(props);

        this.state = {
            failure: null,
            current: null,
        }
    }

    componentDidMount() {
        this.props.get_all_devices();
    }

    componentDidUpdate() {
        if (this.props.current !== null)
            this.props.history.push("/register/device/");
    }

    onSubmit() {
        if (this.state.current === null)
            return this.setState({failure: "Please select a option first"});

        this.props.select_register(this.state.current);
    }

    onChange(e) {
        this.setState({
            failure: null,
            current: parseInt(e.target.value),
        });
    }

    render() {
        return (
            <div>
                <select defaultValue={-1} onChange={this.onChange.bind(this)}>
                    <option disabled={true} value={-1}>Please select a device</option>

                    {this.props.devices.map((device, key) => (
                        <option key={key} value={device.index}>{device.verbose_name}</option>
                    ))}
                </select>

                {this.state.failure}

                <input type="submit" value="Register" onClick={this.onSubmit.bind(this)} />

                {/*{this.props.current !== null ? this.props.context === null ? <RegisterDevice /> : <Context /> : null}*/}

            </div>
        );
    }
}

const mapDispatchToProps = {
    get_all_devices,
    select_register,
};

const mapStateToProps = state => ({
    devices: state.register.devices,
    current: state.register.current,
    context: state.register.context,
});

export default connect(mapStateToProps, mapDispatchToProps)(Register);
