const bcrypt = require('bcryptjs')
const mongoose = require('mongoose')
const Schema = mongoose.Schema

// Create Schema
const UserSchema = new Schema({
	name: {
		type: String,
		required: true
	},
	email: {
		type: String,
		required: true
	},
	password: {
		type: String,
		required: true
	},
	date: {
		type: Date,
		default: Date.now
	}
})
UserSchema.pre('save', function (next) {
	var newUser = this
	bcrypt.genSalt(10, (err, salt) => {
		bcrypt.hash(newUser.password, salt, (err, hash) => {
			if (err) throw err
			newUser.password = hash
			next()
		})
	})
})

UserSchema.methods.comparePassword = function (password, callback) {
	bcrypt.compare(password, this.password, function (err, isMatch) {
		if (err) {
			return callback(err)
		}
		callback(null, isMatch)
	})
}
module.exports = mongoose.model('users', UserSchema)
