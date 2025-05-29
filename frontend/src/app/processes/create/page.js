"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { FaArrowLeft, FaPlus, FaArchive, FaSpinner } from "react-icons/fa";
import { useSearchParams } from "next/navigation";
import api from "@/app/api";
import { useAuth } from "@/context/AuthContext";
import { useSnackbar } from "@/components/SnackbarContext";
import { useRouter } from "next/navigation";

export default function CreateProcessPage() {
  const { showSnackbar } = useSnackbar();
  const FILTER_OPERATORS = [
    { key: "==", label: "Equals", types: ["string", "number"] },
    { key: "!=", label: "Not Equals", types: ["string", "number"] },
    { key: ">", label: "Greater Than", types: ["number"] },
    { key: "<", label: "Lower Than", types: ["number"] },
    { key: ">=", label: "Greater or Equal", types: ["number"] },
    { key: "<=", label: "Lower or Equal", types: ["number"] },
    { key: "contains", label: "Contains", types: ["string"] },
  ];
  const AGGREGATION_OPERATIONS = ["sum", "min", "max", "mean", "count", "median", "std", "var", "first", "last", "unique", "mode", "range"];
  const [loading, setLoading] = useState(false);
  const [repository, setRepository] = useState(null);
  const [isFormValid, setIsFormValid] = useState(false);
  const [processConfig, setProcessConfig] = useState({
    filter: {active: false, parameters: []},
    group: {active: false, parameters: []},
    aggregation: {active: false, parameters: []},
  });
  const [numberParams, setNumbersParams] = useState([]);
  const searchParams = useSearchParams();
  const { token, authLoading } = useAuth();
  const router = useRouter();

  const fetchRepository = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/repositories/?_id=${searchParams.get("repository")}&select=parameters+data_ready+name+version`);
      setRepository(response.data.items[0] || {});
      setNumbersParams(response.data.items[0]?.parameters.filter((p) => p.type === "number") || []);
    } catch (error) {
      if (error.response && (error.response.status === 401 || error.response.status === 403)) {
        showSnackbar("Unauthorized access. Please log in.", "error", false, "bottom-right");
        router.push("/login");
        return;
      }
      showSnackbar("Error fetching repository details", "error", false, "bottom-right");
      console.error("Error fetching repositories:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authLoading) return;
    if (!token) {
      router.push("/login");
      return;
    }
    if (!searchParams.get("repository")) {
      router.push("/");
      return;
    }
    fetchRepository();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, authLoading]);

  useEffect(() => {
    setIsFormValid(isFormValidValue());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [processConfig]);

  const isFormValidValue = () => {
    // At least one action must be active
  const activeActions = Object.keys(processConfig).filter(action => processConfig[action].active);
  if (activeActions.length === 0) return false;

  for (const action of activeActions) {
    const parameters = processConfig[action].parameters;
    // Must have at least one parameter for each active action
    if (!parameters || parameters.length === 0) return false;

    for (const param of parameters) {
      if (action === "filter") {
        // All fields must be filled, and value required for numbers
        if (!param.name || !param.operator || !param.type) return false;
        if (param.type !== "string" && (param.value === undefined || param.value === "")) return false;
      }
      if (action === "group" && !param) return false;
      if (action === "aggregation") {
        // Must have a name, at least one valid operation, and all operations must be valid
        if (!param.name || !param.operations || !param.operations.length) return false;
        if (!param.operations.every(op => AGGREGATION_OPERATIONS.includes(op))) return false;
      }
    }
  }

  return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // TODO: Send to backend
    try {
      setLoading(true);
      await api.post(`/processes/${repository._id.$oid}`, processConfig)
      showSnackbar("Process created successfully", "success", true, "bottom-right");
      showSnackbar("The system will take some time to process the data. You can check the status in the processes page.", "info", false, "bottom-right");
      router.push(`/processes?repository=${repository._id.$oid}`);
    } catch (error) {
      if (error.response && (error.response.status === 401 || error.response.status === 403)) {
        showSnackbar("Unauthorized access. Please log in.", "error", false, "bottom-right");
        router.push("/login");
        return;
      }
      showSnackbar("Error creating process", "error", false, "bottom-right");
      console.error("Error creating process:", error);
    } finally {
      setLoading(false);
    }
    
  };

  const changeActiveActions = (action, active) => {
    setProcessConfig((prev) => ({
      ...prev,
      [action]: {
        parameters: active ? prev[action].parameters : [],
        active: active
      },
    }));
  };

  const capitalize = (string) => string.charAt(0).toUpperCase() + string.slice(1);
  
  const defaultParameter = type => type === "filter" ? {name: "", type: "", operator: "", value: ""} : { name: "", operations: [] };
  
  const addParameter = (type, newParameter) => {
    setProcessConfig((prev) => ({
      ...prev,
      [type]: {
        ...prev[type],
        parameters: newParameter ? Array.from(new Set([...prev[type].parameters, newParameter])) : [...prev[type].parameters, defaultParameter(type)]
      },
    }));
  }

  const changeParameterProperties = (type, index, properties) => {
    setProcessConfig((prev) => ({
      ...prev,
      [type]: {
        ...prev[type],
        parameters: prev[type].parameters.map((param, i) =>
          i === index ? { ...defaultParameter(type), ...properties } : param
        ),
      },
    }));
  };

  const removeParameter = (type, value, index) => {
    setProcessConfig((prev) => ({
      ...prev,
      [type]: {
        ...prev[type],
        parameters: prev[type].parameters.filter((param, i) => value ? value !== param : i !== index),
      },
    }));
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      <Header backgroundColor="bg-orange-500" title="Create Process" />
      <main className="flex-grow max-w-6xl mx-auto w-full px-4 py-8">
        <div className="flex justify-end items-center mb-2">    
          {!loading && repository?._id && <Link
            title="Go Back"
            href={`/processes?repository=${repository?._id.$oid}`}
            className="inline-block bg-orange-500 text-white py-2 px-4 rounded-md hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-600 focus:ring-offset-2"
          >
            <FaArrowLeft className="w-4 h-4" />
          </Link>}
        </div>
        {!loading && repository && <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-bold mb-2">
            <FaArchive className="w-8 h-8 text-orange-500 inline mr-2" /> 
            <a target="_blank" className="text-orange-500 inline" href={`/repositories/show/${repository?._id?.$oid}`}>&nbsp;{repository.name}</a>
          </h2>
          <div className="mb-2"><strong>Version:</strong> {repository.version}</div>
        </div>}
        {!loading && repository?.parameters && <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Configure Process</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Action selection */}
            <div>
              <label className="block font-semibold mb-2">Select Actions (1-3):</label>
              <div className="flex gap-4">
                {Object.keys(processConfig).map((action) => (
                  <label key={action} className="flex items-center gap-1 cursor-pointer">
                    <input
                      type="checkbox"
                      className={`${action === "aggregation" && numberParams.length === 0 ? '': 'cursor-pointer' }`}
                      checked={processConfig[action].active}
                      onChange={(e) => changeActiveActions(action, e.target.checked)}
                      disabled={action === "aggregation" && numberParams.length === 0}
                    />
                    <span className={`${action === "aggregation" && numberParams.length === 0 ? '': 'cursor-pointer' }`} onClick={() => changeActiveActions(action, processConfig[action].active)}>&nbsp;
                      {action === "aggregation" && numberParams.length === 0 ? <del>{capitalize(action)}</del> :capitalize(action)}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Filter action */}
            {processConfig.filter.active && (
              <div className="border rounded p-4 bg-orange-50">
                <div className="font-semibold mb-2">Filter Conditions</div>
                {processConfig.filter.parameters.length > 0 && <div className="overflow-x-auto">
                  <table className="min-w-full bg-white border border-gray-300 rounded-lg shadow-md my-2">
                    <thead>
                      <tr className="bg-orange-500 text-white">
                        <th className="py-3 text-center text-sm font-semibold">Parameter</th>
                        <th className="py-3 text-center text-sm font-semibold">Operator</th>
                        <th className="py-3 text-center text-sm font-semibold">Value</th>
                        <th className="py-3 text-center text-sm font-semibold">&nbsp;</th>
                      </tr>
                    </thead>
                    <tbody>
                      {processConfig.filter.parameters.map((parameter, filterParameterIndex) => {
                        return (
                          <tr key={`filterParameterIndex${filterParameterIndex}`} className="">                      
                            <td className="text-center py-1 px-1">
                              <select
                                className="cursor-pointer border rounded px-2  py-1 min-w-full"
                                value={parameter.name}
                                onChange={(e) => {
                                    const selectedParameter = repository.parameters.find((p) => p.name === e.target.value);
                                    return changeParameterProperties("filter", filterParameterIndex, selectedParameter)
                                  }
                                }
                                placeholder="Select a parameter"
                                required
                              >
                                <option value="" disabled>Select a parameter</option>
                                {repository.parameters.map((p, ) => (
                                  <option key={`filterParameter${filterParameterIndex}Parameter${p.name}`} value={p.name}>
                                    {p.name}
                                  </option>
                                ))}
                              </select>
                            </td>
                            <td className="text-center py-1 px-1">
                              <select
                                className="cursor-pointer border rounded px-2 py-1 min-w-full"
                                value={parameter.operator}
                                onChange={(e) =>
                                  changeParameterProperties("filter", filterParameterIndex, {name: parameter.name, type: parameter.type, operator: e.target.value})
                                }
                                placeholder="Select an operator"
                                required
                                disabled={!parameter.name}
                              >
                                <option value="" disabled>Select an operator</option>
                                {FILTER_OPERATORS.filter((op) =>
                                  parameter.type ? op.types.includes(parameter.type) : true
                                ).map((op) => (
                                  <option key={`filterOperator${filterParameterIndex}Operator${op.key}`} value={op.key}>
                                    {op.label}
                                  </option>
                                ))}
                              </select>
                            </td>
                            <td className="text-center py-1 px-1">
                              <input
                                className="border rounded px-2 py-1 min-w-full"
                                type={parameter.type === "number" ? "number" : "text"}
                                value={parameter.value}
                                onChange={(e) =>
                                  changeParameterProperties("filter", filterParameterIndex, {name: parameter.name, type: parameter.type, operator: parameter.operator, value: e.target.value ? (parameter.type === "number" ? Number(e.target.value) : String(e.target.value)) : ""})
                                }
                                placeholder="Insert condition value"
                                required={parameter.type !== "string" && parameter.operator !== "===" && parameter.operator !== "!=="}
                                disabled={!parameter.name || !parameter.type}
                              />
                            </td>
                            <td className="text-center py-1 px-1">
                              <button
                                type="button"
                                title="Remove filter condition"
                                className="cursor-pointer bg-red-500 hover:bg-red-600 font-bold px-2 text-white rounded text-sm focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2"
                                onClick={() => removeParameter("filter", null, filterParameterIndex)}
                              >
                                ×
                              </button>
                            </td>
                          </tr>
                        );
                      })}                    
                    </tbody>
                  </table>
                </div>}
                <button
                  type="button"
                  className="cursor-pointer bg-orange-500 text-white px-3 py-1 rounded mt-2 hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-600 focus:ring-offset-2"
                  onClick={() => addParameter("filter")}
                >
                  Add Filter Condition
                </button>
              </div>
            )}

            {/* Group action */}
            {processConfig.group.active && (
              <div className="border rounded p-4 bg-orange-50">
                <div className="font-semibold mb-2">Group By Parameters</div>
                <div className="flex flex-wrap gap-3">
                  {repository.parameters.map((parameter) => (
                    <label key={`groupByParameter${parameter.name}`} className="flex items-center gap-1 cursor-pointer">
                      <input
                        type="checkbox"
                        className="cursor-pointer"
                        checked={processConfig.group.parameters.includes(parameter.name)}
                        onChange={e => e.target.checked ? addParameter("group", parameter.name) : removeParameter("group", parameter.name)}
                      />
                      <span className="cursor-pointer" onClick={() => processConfig.group.parameters.includes(parameter.name) ? addParameter("group", parameter.name) : removeParameter("group", parameter.name)}>&nbsp;{parameter.name}</span>
                    </label>
                  ))}
                </div>
                {processConfig.group.parameters.length === 0 && (
                  <div className="text-red-600 text-sm mt-2">Select at least one parameter to group by.</div>
                )}
              </div>
            )}

            {/* Aggregation action */}
            {processConfig.aggregation.active && (
              <div className="border rounded p-4 bg-orange-50">
                <div className="font-semibold mb-2">Aggregation</div>
                {processConfig.aggregation.parameters.map((aggregation, aggregationIndex) => (
                  <div key={`aggregation${aggregationIndex}`} className="overflow-x-auto">
                    <div  className="flex gap-2 items-center mb-2">
                      <label className="font-semibold min-w-1/3 ">Parameter</label>
                      <label className="font-semibold min-w-3/5 text-center">Operations</label>
                    </div>
                    <div  className="flex gap-2 items-center mb-2">
                      <select
                        className="cursor-pointer border rounded px-2 py-1"
                        value={aggregation.name}
                        placeholder="Select a parameter"
                        onChange={e => changeParameterProperties("aggregation", aggregationIndex, {name: e.target.value})}
                        required
                      >
                        <option value="" disabled>Select a parameter</option>
                        {numberParams.filter(numberParam => numberParam.name === aggregation.name || !processConfig.aggregation.parameters.find(aggParam => aggParam.name === numberParam.name)).map((p) => (
                          <option key={`aggreration${aggregationIndex}Parameter${p.name}`} value={p.name}>
                            {p.name}
                          </option>
                        ))}
                      </select>
                      {aggregation.name && <div className="flex items-betweeen rounded mb-2 gap-2 pt-2">
                        {aggregation.operations.map((operation, operationIndex) => (
                          <div key={`aggregation${aggregationIndex}Operation${operationIndex}`} className="flex items-betweeen">
                            <select
                              className="cursor-pointer border rounded px-2 py-1"
                              value={operation}
                              placeholder="Select an operation"
                              onChange={(e) => {
                                const updatedOperations = aggregation.operations;
                                updatedOperations[operationIndex] = e.target.value;
                                return changeParameterProperties(
                                  "aggregation",
                                  aggregationIndex,
                                  {name: aggregation.name, operations: updatedOperations}
                                )}
                              }
                              required
                              disabled={!aggregation.name}
                            >
                              <option value="" disabled>Select an operation</option>
                              {AGGREGATION_OPERATIONS.filter(op => operation === op || !processConfig.aggregation.parameters[aggregationIndex].operations.find(operationItem => operationItem === op)).map((op) => (
                                <option key={`aggregation${aggregationIndex}Operation${operation}Option${op}`} value={op}>
                                  {op}
                                </option>
                              ))}
                            </select>
                            <button
                              type="button"
                              title="Remove operation"
                              className="cursor-pointer font-bold text-sm bg-red-500 hover:bg-red-600 w-6 h-6 mt-1 rounded-full text-white ml-1 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2"
                              onClick={() => {
                                const operationToRemove = processConfig.aggregation.parameters[aggregationIndex].operations[operationIndex];
                                const updatedOperations = processConfig.aggregation.parameters[aggregationIndex].operations.filter(opItem => opItem !== operationToRemove);
                                return changeParameterProperties(
                                  "aggregation",
                                  aggregationIndex,
                                  {name: aggregation.name, operations: updatedOperations}
                                )
                              }}>
                              ×
                            </button>
                          </div>
                        ))}
                        {aggregation.operations.length < AGGREGATION_OPERATIONS.length && <button
                          type="button"
                          title="Add operation"
                          className="cursor-pointer font-bold px-2 text-sm bg-orange-500 hover:bg-orange-600 rounded text-white py-1 px-1 focus:outline-none focus:ring-2 focus:ring-orange-600 focus:ring-offset-2"
                          onClick={() => changeParameterProperties(
                            "aggregation",
                            aggregationIndex,
                            {name: aggregation.name, operations: [...aggregation.operations, ""]}
                          )}
                        >
                          <FaPlus className="inline" />
                          {aggregation.operations.length === 0 && <span>&nbsp;Add operation</span>}
                        </button>}
                      </div>}
                      <button
                        type="button"
                        title="Remove aggregation"
                        className="cursor-pointer font-bold px-2  text-lg bg-red-500 hover:bg-red-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2"
                        onClick={() => removeParameter("aggregation", null, aggregationIndex)}
                      >
                        ×
                      </button>
                    </div>
                  </div>
                ))}
                {processConfig.aggregation.parameters.length < numberParams.length && (
                  <button
                    type="button"
                    className="cursor-pointer bg-orange-500 text-white px-3 py-1 rounded mt-2 hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-600 focus:ring-offset-2"
                    onClick={() => addParameter("aggregation")}
                  >
                    Add Aggregation
                  </button>
                )}
                {numberParams.length === 0 && (
                  <div className="text-red-600 text-sm mt-2">No numeric parameters available for aggregation.</div>
                )}
              </div>
            )}

            <button
              type="submit"
              className={` bg-orange-500 text-white py-2 px-4 rounded ${isFormValid ? "cursor-pointer hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-600 focus:ring-offset-2" : "opacity-50 cursor-not-allowed"}`}
              disabled={!isFormValid || loading}
            >
              {!loading && <FaPlus className="inline mr-2" />}
              {loading && <FaSpinner className="animate-spin inline mr-2 white" />}
              Create Process
            </button>
          </form>
        </div>}
      </main>
      <Footer backgroundColor="bg-orange-500" />
    </div>
  );
}
