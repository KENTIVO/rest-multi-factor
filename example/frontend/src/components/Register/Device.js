import React from "react";
import PropTypes from "prop-types";

import { connect } from "react-redux";

import { submit_registration } from "../../actions/submit";


class Device extends React.Component {
    static propTypes = {
        context: PropTypes.object,
        current: PropTypes.number.isRequired,
        options: PropTypes.object.isRequired,

        submit_registration: PropTypes.func.isRequired,
    };

    componentDidMount() {
        if (Object.values(this.props.options).every(o => !o.write_only || o.read_only))
            this.props.submit_registration(this.props.current);
    }

    componentDidUpdate() {
        if (this.props.context !== null)
            this.props.history.push("/register/context/");
    }

    *fields() {
        const names = Object.keys(this.props.options).filter(index => {
            return this.props.options[index].write_only || !this.props.options[index].read_only
        });

        for (let i=0; i < names.length; i++) {
            yield <input name={names[i]} type="text" />;
        }
    }

    render() {
        return (
            <div>
                {[...this.fields()]}
            </div>
        );
    }
}

const mapStateToProps = state => ({
    current: state.register.current,
    context: state.register.context,
    options: state.register.options,
});

export default connect(mapStateToProps, {submit_registration})(Device);
