import {LooseParser as Parser} from "./acorn/acorn-loose/dist/acorn-loose.mjs"

function forToWhile(node) {
    console.assert(node.type === 'ForStatement', "is given node a for statement")
    const newNode = {type: 'BlockStatement', start: 0, end: 0, body: []}
    newNode.body.push(initUpdateToExpr(node.init))  // add initializer

    let newBody
    if (node.body.type === 'BlockStatement') {
        newBody = {...node.body}
    } else {
        newBody = {type: 'BlockStatement', start: 0, end: 0, body: [{...node.body}]}
    }
    newBody.body.push(initUpdateToExpr(node.update))

    const whileNode = {type: 'WhileStatement', start: 0, end: 0, test: node.test, body: newBody}

    newNode.body.push(whileNode)
    return newNode
}

function selfAssignToUpdateAndInplace(node) {
    console.assert(node.type === 'AssignmentExpression', "is given node a assignment statement")
    const left = node.left
    const right = node.right

    if (node.operator === '+=' && right.type === 'Literal') {
        if (right.value === 1) {
            return {type: 'UpdateExpression', start: 0, end: 0, argument: left, operator: '++', prefix: false}
        } else if (right.value === -1) {
            return {type: 'UpdateExpression', start: 0, end: 0, argument: left, operator: '--', prefix: false}
        }
    } else if (node.operator === '-=' && right.type === 'Literal') {
        if (right.value === 1) {
            return {type: 'UpdateExpression', start: 0, end: 0, argument: left, operator: '--', prefix: false}
        } else if (right.value === -1) {
            return {type: 'UpdateExpression', start: 0, end: 0, argument: left, operator: '++', prefix: false}
        }
    }

    if (node.operator !== '=' || right.type !== 'BinaryExpression') return node

    if (right.operator === '+') {
        let another
        if (isSameValue(left, right.left)) {
            another = right.right
        }
        if (isSameValue(left, right.right)) {
            another = right.left
        }
        if (another !== undefined) {
            if (another.type === 'Literal' && another.value === 1) {
                return {type: 'UpdateExpression', start: 0, end: 0, argument: left, operator: '++', prefix: false}
            } else if (another.type === 'UnaryExpression' && another.operator === '-' && another.argument.value === 1) {
                return {type: 'UpdateExpression', start: 0, end: 0, argument: left, operator: '--', prefix: false}
            }
            return {type: 'AssignmentExpression', start: 0, end: 0, left: left, operator: '+=', right: another}
        }
    } else if (right.operator === '-') {
        if (isSameValue(left, right.left)) {
            let another = right.right
            if (another.type === 'Literal' && another.value === 1) {
                return {type: 'UpdateExpression', start: 0, end: 0, argument: left, operator: '--', prefix: false}
            } else if (another.type === 'UnaryExpression' && another.operator === '-' && another.argument.value === 1) {
                return {type: 'UpdateExpression', start: 0, end: 0, argument: left, operator: '++', prefix: false}
            }
            return {type: 'AssignmentExpression', start: 0, end: 0, left: left, operator: '-=', right: another}
        }
    } else if (right.operator === '*') {
        let another
        if (isSameValue(left, right.left)) {
            another = right.right
        }
        if (isSameValue(left, right.right)) {
            another = right.left
        }
        if (another !== undefined) return {
            type: 'AssignmentExpression',
            start: 0,
            end: 0,
            left: left,
            operator: '+=',
            right: another
        }
    } else if (right.operator === '/') {
        if (isSameValue(left, right.left)) {
            if (right.right.type === 'UnaryExpression' && right.right.operator === '-' && right.right.argument.value === 1) {
                return {type: 'AssignmentExpression', start: 0, end: 0, left: left, operator: '*=', right: right.right}
            }
            return {type: 'AssignmentExpression', start: 0, end: 0, left: left, operator: '/=', right: right.right}
        }
    } else if (right.operator === '%') {
        if (isSameValue(left, right.left)) {
            return {type: 'AssignmentExpression', start: 0, end: 0, left: left, operator: '%=', right: right.right}
        }
    }
    return node
}

function isSameValue(left, right) {
    if (left.type !== right.type) return false
    if (left.type === 'Literal') return left.value === right.value
    if (left.type === 'Identifier') return left.name === right.name
    if (left.type === 'MemberExpression') return isSameValue(left.object, right.object) && isSameValue(left.property, right.property)
}

function initUpdateToExpr(node) {
    if (node.type === 'VariableDeclaration') return {...node}
    return {type: 'ExpressionStatement', start: 0, end: 0, expression: {...node}}
}

function convertAll(node) {
    if (Array.isArray(node.body)) {
        for (let i = 0; i < node.body.length; i++) {
            node.body[i] = convertAll(node.body[i])
        }
    } else if (node.body !== undefined) {
        node.body = convertAll(node.body)
    }
    return convert(node)
}

function convert(node) {
    if (node.type === 'ForStatement') {
        return convertAll(forToWhile(node))
    }
    if (node.type === 'ExpressionStatement' && node.expression.type === 'AssignmentExpression') {
        return {...node, expression: selfAssignToUpdateAndInplace(node.expression)}
    }

    return node
}

function ConvertAllCode(code) {
    let newNode = convertAll(Parser.parse(code, {ranges: false}));
    return escodegen.generate(newNode)
}

function ConvertAllToNode(code) {
    return convertAll(Parser.parse(code, {ranges: false}));
}

function RunAssertions(question, node_) {
    const failure = []
    const parsedAssertions = []
    question.assertions.forEach(assertion => {
        parsedAssertions.push({...assertion, assertion: JSON.parse(assertion.assertion)})
    })
    const nodes = new NodeWalker().walkNode(node_)
    nodes.forEach(node => {
        parsedAssertions.forEach(assertion => {
            RecursiveCompare(assertion.assertion, node)
        })
    })
    parsedAssertions.forEach(assertion => {
        RecursiveDetermine(assertion.assertion)
        console.log(assertion)
        if (assertion.assertion.matched === false || (!assertion.assertion.hasOwnProperty('none') && !assertion.assertion.matched)) {
            failure.push(assertion)
        }
    })

    return failure
}

function RecursiveCompare(assertion, node) {
    if (assertion.matched !== undefined) return assertion.matched
    let [none, oneOf, all, is_container] = [false, false, false, 0]

    if (assertion.hasOwnProperty('none')) {
        is_container++
        none = assertion.none.some(a => RecursiveCompare(a, node))
    }
    if (assertion.hasOwnProperty('oneOf')) {
        is_container++
        oneOf = assertion.oneOf.some(a => RecursiveCompare(a, node))
    }
    if (assertion.hasOwnProperty('all')) {
        is_container++
        assertion.all.forEach(a => RecursiveCompare(a, node))
        all = assertion.all.every(a => a.matched)
    }

    if (is_container > 1){
        console.warn('not only 1 or none of [none, oneOf, all] is given: ' + JSON.stringify(assertion))
    }
    if (is_container) {
        if (none) assertion.matched = false
        else if (oneOf) assertion.matched = true
        else if (all) assertion.matched = true
    } else if (CheckAssertionSame(assertion, node)) {
        assertion.matched = true
    }

    return assertion.matched
}

function RecursiveDetermine(assertion) {
    if (assertion.hasOwnProperty('none')) {
        assertion.none.forEach(a => RecursiveDetermine(a))
        assertion.matched = !assertion.none.some(a => a.matched)
    } else if (assertion.hasOwnProperty('oneOf')) {
        assertion.oneOf.some(a => RecursiveDetermine(a))
        assertion.matched = assertion.oneOf.some(a => a.matched)
    } else if (assertion.hasOwnProperty('all')) {
        assertion.all.forEach(a => RecursiveDetermine(a))
        assertion.matched = assertion.all.every(a => a.matched)
    }

    if (!assertion.matched) assertion.matched = false
}

function CheckAssertionSame(assertion, node) {
    if (typeof node !== 'object' || node === null) return false
    for (const [key, val] of Object.entries(assertion)) {
        if (val === null) {
            if (node[key] !== null) return false
        } else if (['Number', 'String', 'Boolean', 'Symbol'].includes(val.constructor.name)) {
            if (assertion[key] !== node[key]) return false
        } else if (val.hasOwnProperty('allow')) {
            if (val.allow.indexOf(node[key]) === -1) return false
        } else if (Array.isArray(val)) {
            if (!Array.isArray(node[key])) return false
            if (val.length !== node[key].length) return false
            for (let i = 0; i < val.length; i++) {
                if (!CheckAssertionSame(val[i], node[key][i])) return false
            }
        } else if (typeof val === 'object') {
            let target = node[key]
            if (Array.isArray(target)) {
                if (target.length === 1) target = target[0]
                else console.warn(`node.'${key}' is not 1-length array`)
            }
            if (!CheckAssertionSame(val, target)) return false
        }
    }
    return true
}

class NodeWalker {
    constructor() {
        this.queue = []
    }

    walkNode(node) {
        if (node === undefined || node === null) return
        if (!Array.isArray(node) && typeof node === 'object') {
            this.queue.push(node)
        }
        for (const [_, val] of Object.entries(node)) {
            if (Array.isArray(val)) {
                val.forEach(el => {
                    this.walkNode(el)
                })
            } else if (typeof val === 'object') {
                this.walkNode(val)
            }
        }
        return this.queue
    }
}

export {ConvertAllCode, ConvertAllToNode, RunAssertions}